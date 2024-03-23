from etcd3 import client

etcd_client = client('localhost', 2379)

def get_value(key):
    response, _ = etcd_client.get(key)
    if response is not None:
        print(response.decode())
    else:
        print("Key not found")

def put_key_value(key, value):
    etcd_client.put(key, value)

put_key_value('/mykey', 'myvalue')
get_value('/mykey')