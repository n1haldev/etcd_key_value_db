from etcd3 import client
import types

client = client(host="localhost", port=2379, grpc_options={
                        'grpc.http2.true_binary': 0,
                    }.items())

# client.put("/name", "nihal t m")
# client.put("/name", "nihal t m")
# client.put("/number", "1234567890")
# client.put("/articles", "3")

# val = client.get("/articles")[0].decode()
# print(val)

data = client.get_all()
print(type(data))

for k,v in data:
    print(k, v)



# print(data)
# print(data.decode())