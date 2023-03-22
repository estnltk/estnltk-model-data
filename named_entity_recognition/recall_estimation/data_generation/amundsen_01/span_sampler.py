from random import sample, choices
from estnltk.storage.postgres import LayerQuery, IndexQuery
from tqdm import tqdm

class SpanSampler:

    def __init__(self, storage, collection, layer, attribute,termsfile):
        self.storage = storage
        self.conn = storage.conn
        self.cur = self.conn.cursor()
        self.collection = collection
        self.layer = layer
        self.attribute = attribute
        self.terms = []
        with open(termsfile, 'r', encoding='UTF-8') as f:
            term = f.readline()
            while term is not '':
                self.terms.append(term.strip())
                term = f.readline()

    def __call__(self, count, attribute, return_index=False, with_replacement=True):
        # Returns iterator of type Text, Span or int, Text, span
        # count determines the number of samples
        # with replacement means that same span can be sampled several times
        self.conn.commit()
        self.create_sampling_matrix(attribute)
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

    def attribute_locations_creation(self):
        self.conn.commit()
        self.cur.execute("""SELECT EXISTS (
           SELECT FROM information_schema.tables 
           WHERE  table_schema = 'public'
           AND    table_name   = 'attribute_locations'
           );""")
        res = self.cur.fetchall()
        if not res[0][0]:
            self.cur.execute(
                "CREATE TABLE attribute_locations (layer_id integer, attribute_value varchar, indices integer[], count integer);")
            self.conn.commit()
            for term in self.terms:
                q = LayerQuery('v172_geo_terms', lemma=term)
                for key, txt in tqdm(self.collection.select(query=q, layers=['v172_geo_terms'])):
                    indices = [i for i, nertag in enumerate(txt['v172_geo_terms']['lemma']) if nertag[0] == term]
                    self.cur.execute(
                        "INSERT INTO attribute_locations (layer_id, attribute_value,indices,count) VALUES (%s, %s, %s, %s)",
                        (key, term, indices, len(indices)))

        self.conn.commit()

    def create_sampling_matrix(self, attribute_val):
        self.cur.execute("CREATE TABLE sampling_matrix (id serial, layer integer, layer_index integer);")
        self.cur.execute(
            "INSERT INTO sampling_matrix (layer,layer_index) (SELECT layer_id as layer, unnest(indices) as layer_index FROM attribute_locations WHERE attribute_value IN " + str(
                attribute_val) + ");")
        self.conn.commit()

    def find_sampled_indices(self, count, with_replacement):
        self.cur.execute("SELECT COUNT(*) FROM sampling_matrix;")
        span_count = self.cur.fetchall()[0][0]
        self.conn.commit()
        if with_replacement:
            sampled = choices(range(span_count), k=count)
        else:
            sampled = sample(range(span_count), count)
        self.cur.execute("SELECT * FROM sampling_matrix WHERE id IN " + str(tuple(sampled)) + ';')
        return self.cur.fetchall()

    def clear_sampling_matrix(self):
        self.conn.commit()
        self.cur.execute("DROP TABLE sampling_matrix;")
        self.conn.commit()
