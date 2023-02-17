class Mapping:
    def __init__(self, collection_path, table_name):
        self.collection_path = collection_path
        self.table_name = table_name

    def get_collection_path(self):
        return self.collection_path

    def get_table_name(self):
        return self.table_name
