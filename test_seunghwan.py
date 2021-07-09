from  ppadb.client  import  Client  as  AdbClient 
# 기본값은 "127.0.0.1"이고 5037 
client  =  AdbClient ( host = "127.0.0.1" ,  port = 5037 ) 
print ( client . version ()) 
