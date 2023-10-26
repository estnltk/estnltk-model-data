import configparser
import os, os.path

from estnltk.storage.postgres import PostgresStorage


def load_configuration(config_file):
    config = configparser.ConfigParser()

    file_name = os.path.abspath(os.path.expanduser(os.path.expandvars(str(config_file))))

    if not os.path.exists(file_name):
        raise ValueError("File {file} does not exist".format(file=str(config_file)))

    if len(config.read(file_name)) != 1:
        raise ValueError("File {file} is not accessible or is not in valid INI format".format(file=config_file))

    for option in ["host", "port", "database", "username", "password", "role", "schema", "collection"]:
        if not config.has_option('source_database', option):
            prelude = "Error in file {}\n".format(file_name) if len(file_name) > 0 else ""
            raise ValueError(
                "{prelude}Missing option {option} in the section [{section}]".format(
                    prelude=prelude, option=option, section='source_database'
                )
            )

    config.read(file_name)
    
    return config


def connect_to_database(config):

    dbname = config['source_database']['database']
    user = config['source_database']['username']
    password = config['source_database']['password']
    host = config['source_database']['host']
    port = config['source_database']['port']
    role = config['source_database']['role']
    schema = config['source_database']['schema']
    collection = config['source_database']['collection']


    storage = PostgresStorage(host=host,
                              port=int(port),
                              dbname=dbname,
                              user=user,
                              password=password,
                              schema=schema,
                              role=role,
                              temporary=False)
    return storage

def load_local_configuration(config_file):
    
    config = configparser.ConfigParser()

    file_name = os.path.abspath(os.path.expanduser(os.path.expandvars(str(config_file))))

    if not os.path.exists(file_name):
        raise ValueError("File {file} does not exist".format(file=str(config_file)))

    if len(config.read(file_name)) != 1:
        raise ValueError("File {file} is not accessible or is not in valid INI format".format(file=config_file))

    for option in ["sqlite_file"]:
        if not config.has_option('local_database', option):
            prelude = "Error in file {}\n".format(file_name) if len(file_name) > 0 else ""
            raise ValueError(
                "{prelude}Missing option {option} in the section [{section}]".format(
                    prelude=prelude, option=option, section='local_database'
                )
            )

    config.read(file_name)
    
    return config
