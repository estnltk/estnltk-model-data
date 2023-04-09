from random import sample, choices
from estnltk.storage.postgres import LayerQuery, IndexQuery
from tqdm import tqdm

class SpanSampler:
    
    def __init__(self, storage, collection, layer, attribute):
        self.storage = storage
        self.conn = storage.conn
        self.cur = self.conn.cursor()
        self.collection = collection
        self.layer = layer
        self.attribute = attribute
    
    def __call__(self, count, attribute, return_index=False, with_replacement=False): 
        # Returns iterator of type Text, Span or int, Text, span
        # count determines the number of samples
        # with replacement means that same span can be sampled several times
        self.attribute_locations_creation()
        self.conn.commit()
        self.create_sampling_matrix(attribute)
        indices = self.find_sampled_indices(count,with_replacement)
        result_list = []
        only_txt_index = [idx[1] for idx in indices]
        texts = list(collection.select( query=IndexQuery(only_txt_index),layers=[self.layer],return_index=True ))
        for text in texts:
            idx = [index for index in indices if text[0] == index[1]][0]
            if return_index:
                result_list.append((idx[0],text[1],idx[1:]))
            else:
                result_list.append((text[1],idx[1:]))
        self.clear_sampling_matrix()
        return result_list
    
    def attribute_locations_creation(self):
        self.conn.commit()
        self.cur.execute("""SELECT EXISTS (
           SELECT FROM information_schema.tables 
           WHERE  table_schema = 'public'
           AND    table_name   = 'attribute_locations_pos'
           );""")
        res = self.cur.fetchall()
        if not res[0][0]:
            self.cur.execute("CREATE TABLE attribute_locations_pos (layer_id integer, attribute_value varchar, prev_pos varchar, startidx integer, endidx integer);")
            self.conn.commit()
            for term in terms:
                q = LayerQuery('v172_geo_terms', lemma=term)
                for key, txt in tqdm(collection.select(query=q,layers=['v172_geo_terms'])):
                    txt.tag_layer()
                    for i,word in enumerate(txt.words):
                        if term in word.lemma:
                            prev_pos = txt.partofspeech[i-1]
                            start = txt.words[i-1].start
                            end = word.end
                            self.cur.execute("INSERT INTO attribute_locations_pos (layer_id, attribute_value,prev_pos,startidx,endidx) VALUES (%s, %s, %s, %s, %s)",(key, term, prev_pos[0],start,end))
        self.conn.commit()

        
    def create_sampling_matrix(self,attribute_val):
        self.cur.execute("CREATE TABLE sampling_matrix (id serial, layer integer, startidx integer, endidx integer, attribute varchar);")
        self.cur.execute("INSERT INTO sampling_matrix (layer,startidx,endidx,attribute) (SELECT layer_id as layer, startidx, endidx, prev_pos FROM attribute_locations_pos WHERE prev_pos IN " + str(attribute_val) + ");")
        self.conn.commit()
    
    def find_sampled_indices(self,count,with_replacement):
        self.cur.execute("SELECT COUNT(*) FROM sampling_matrix;")
        span_count = self.cur.fetchall()[0][0]
        self.conn.commit()
        if count > span_count:
            count = span_count
        if with_replacement:
            sampled = choices(range(span_count),k=count)
        else:
            sampled = sample(range(span_count),count)
        self.cur.execute("SELECT * FROM sampling_matrix WHERE id IN " + str(tuple(sampled)) + ';')
        return self.cur.fetchall()
    
    def clear_sampling_matrix(self):
        self.conn.commit()
        self.cur.execute("DROP TABLE sampling_matrix;")
        self.conn.commit()
        
    def clear_attr_loc(self):
        self.conn.commit()
        self.cur.execute("DROP TABLE attribute_locations_pos;")
        self.conn.commit()
        