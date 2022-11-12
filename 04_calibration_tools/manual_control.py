import local_coms

z = local_coms.LOCAL_COMS_MASTER()

while True:
    text = input("Enter cmd: ")
    reply, status, t = z.msg_text(text)
    print(reply, status, t)
    print()        
              
