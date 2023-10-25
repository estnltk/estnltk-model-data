from random import Random
from random import sample, choices
import sqlite3
import warnings

from tqdm import tqdm

from estnltk.storage.postgres import LayerQuery, IndexQuery
from estnltk.storage.postgres import PgCollection


class SpanSampler:

    def __init__(self, collection, layer, attribute, termsfile, db_file_name='geo_terms_sample.db', seed=1, verbose=False):
        self.verbose = verbose
        # Use local sqlite3 database for sampling
        assert isinstance(db_file_name, str)
        self._db_file_name = db_file_name
        self._connection = sqlite3.connect(self._db_file_name)
        self._cursor = self._connection.cursor()
        # Use data from a PostgreSQL collection
        assert isinstance(collection, PgCollection), \
            f'(!) Unexpected data type {type(collection)!r} for collection. '+\
            f'Expected estnltk.storage.postgres.PgCollection.'
        self.collection = collection
        self.layer = layer
        self.attribute = attribute
        self.terms = []
        self.random = Random()
        self.random.seed( seed )
        with open(termsfile, 'r', encoding='UTF-8') as in_f:
            for line in in_f:
                if len(line.strip()) > 0:
                    self.terms.append( line.strip() )
        if self.verbose:
            print(f'Loaded {len(self.terms)} terms from {termsfile}.')

    # =====================================================================
    #   attribute_locations table (used as a basis for sampling)
    # =====================================================================

    def attribute_locations_table_exists(self):
        self._cursor.execute("""SELECT EXISTS (
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='attribute_locations' 
            ORDER BY name );
        """)
        res = self._cursor.fetchall()
        return res[0][0]

    def create_attribute_locations_table(self):
        if not self.attribute_locations_table_exists():
            self._cursor.execute(
                "CREATE TABLE attribute_locations (layer_id integer, attribute_value varchar, span_index integer, total_spans integer);")
            self._connection.commit()
            if self.verbose:
                print(f'\nIndexing terms ...\n')
            for term in self.terms:
                if self.verbose:
                    print(f'\nSearching for term {term!r} ...\n')
                q = LayerQuery(self.layer, **{self.attribute: term})
                for key, txt in tqdm(self.collection.select(query=q, layers=[self.layer])):
                    indices = [i for i, nertag in enumerate(txt[self.layer][self.attribute]) if nertag[0] == term]
                    rows = [ (key, term, i, len(indices)) for i in indices ]
                    self._cursor.executemany(
                        "INSERT INTO attribute_locations (layer_id, attribute_value, span_index, total_spans) VALUES (?, ?, ?, ?)", rows )
                    self._connection.commit()
        else:
            warnings.warn(f'(!) {self._db_file_name!r} already contains attribute_locations table. Skipping the table creation.')

    # Find counts of all attribute values
    def get_attribute_counts(self):
        if not self.attribute_locations_table_exists():
            raise Exception('(!) attribute_locations table has not been generated yet.')
        self._cursor.execute("SELECT attribute_value, COUNT(attribute_value) FROM attribute_locations GROUP BY attribute_value;")
        return self._cursor.fetchall()

    # Find counts of attribute values grouped by layer_id (each layer counted only once)
    #@deprecated
    def get_attribute_counts_by_layer_id(self):
        if not self.attribute_locations_table_exists():
            raise Exception('(!) attribute_locations table has not been generated yet.')
        self._cursor.execute("""
        SELECT a.attribute_value, COUNT(a.attribute_value) FROM (
            SELECT layer_id, attribute_value FROM attribute_locations GROUP BY layer_id 
        ) AS a GROUP BY a.attribute_value;
        """)
        return self._cursor.fetchall()

    # Find all distinct layer_id-s annotated by attributes/spans
    def get_attribute_layer_ids(self, normalize=True):
        if not self.attribute_locations_table_exists():
            raise Exception('(!) attribute_locations table has not been generated yet.')
        self._cursor.execute("SELECT DISTINCT layer_id FROM attribute_locations;")
        results = self._cursor.fetchall()
        if normalize:
            # Get rid of tuple data structures, output only integers
            results = [res_tuple[0] for res_tuple in results]
        return results

    def clear_attribute_locations(self):
        self._cursor.execute("DROP TABLE attribute_locations;")
        self._connection.commit()

    # =====================================================================
    #   sampling_matrix table (temporary, used only during sampling)
    # =====================================================================

    def sampling_matrix_table_exists(self):
        self._cursor.execute("""SELECT EXISTS (
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='sampling_matrix' 
            ORDER BY name );
        """)
        res = self._cursor.fetchall()
        return res[0][0]

    def create_sampling_matrix(self, attribute_val):
        self._cursor.execute("CREATE TABLE sampling_matrix (id INTEGER PRIMARY KEY AUTOINCREMENT, layer INTEGER, span_index INTEGER);")
        self._cursor.execute(
            "INSERT INTO sampling_matrix (layer, span_index) SELECT layer_id as layer, span_index FROM attribute_locations WHERE attribute_value IN " + str(
                attribute_val) + ";")
        self._connection.commit()

    def __call__(self, count, attribute_values, return_index=False, with_replacement=True):
        '''
        Samples given amount of spans that meet given conditions (satisfy attribute_values). 
        If with_replacement is True (default) then same span can be sampled several times. 
        If return_index is True than adds text_ids to the results (default: False).
        Returns list of type (Text, span) or (int, Text, span).
        '''
        if not self.attribute_locations_table_exists():
            self.create_attribute_locations_table()
        if self.sampling_matrix_table_exists():
            self.clear_sampling_matrix()
        self.create_sampling_matrix(attribute_values)
        indices = self.find_sampled_indices(count, with_replacement)
        result_list = []
        only_txt_index = [idx[1] for idx in indices]
        texts = list(self.collection.select(query=IndexQuery(only_txt_index), layers=[self.layer], return_index=True))
        for text in texts:
            idx = [index for index in indices if text[0] == index[1]][0]
            if return_index:
                result_list.append((idx[0], text[1], text[1][self.layer][idx[2]]))
            else:
                result_list.append((text[1], text[1][self.layer][idx[2]]))
        self.clear_sampling_matrix()
        return result_list

    def find_sampled_indices(self, count, with_replacement):
        # find sample size
        self._cursor.execute("SELECT COUNT(*) FROM sampling_matrix;")
        total_span_count = self._cursor.fetchall()[0][0]
        # find matrix starting index
        self._cursor.execute("SELECT * FROM sampling_matrix LIMIT 1;")
        start_index = self._cursor.fetchall()[0][0]
        # draw sample
        if count > total_span_count:
            count = total_span_count
        if with_replacement:
            sampled = self.random.choices(range(total_span_count), k=count)
        else:
            sampled = self.random.sample(range(total_span_count), count)
        # correct indexes
        if start_index > 0:
            sampled = [i+start_index for i in sampled]
            assert all([i <= total_span_count for i in sampled])
        # fetch sample
        self._cursor.execute("SELECT * FROM sampling_matrix WHERE id IN " + str(tuple(sampled)) + ';')
        return self._cursor.fetchall()

    def clear_sampling_matrix(self):
        self._cursor.execute("DROP TABLE sampling_matrix;")
        self._connection.commit()
