import ldap
from ldap import modlist

l = ldap.initialize('ldap://172.17.0.2')
binddn = "cn=admin,dc=example,dc=org"
pw = "admin"
basedn = "dc=example,dc=org"
basedn = "dc=example,dc=org"
searchFilter = "(objectClass=simpleSecurityObject)"
searchAttribute = ["description"] # ["mail","department"]
#this will scope the entire subtree under UserUnits
searchScope = ldap.SCOPE_SUBTREE
#Bind to the server
try:
    l.protocol_version = ldap.VERSION3
    l.simple_bind_s(binddn, pw)
except ldap.INVALID_CREDENTIALS:
  print("Your username or password is incorrect.")
  sys.exit(0)
except ldap.LDAPError as e:
  if type(e.message) == dict and e.message.has_key('desc'):
      print (e.message['desc'])
  else:
      print (e)
  sys.exit(0)

try:
  amL = modlist.addModlist( {'objectClass': [b'simpleSecurityObject', b'organizationalRole'], 'cn': [b'mikkamakka'], 'description': [b'LDAP user'], 'userPassword': [b'{SSHA}rihiGNX6wWYu5OFdcILnBU0835giWJzH']})
  res = l.add_s("cn=mikkamakka,"+basedn,amL)

  print("Addresult: "+str(l.result2(res)))
except ldap.LDAPError as e:
    print (e)


try:
    ldap_result_id = l.search(basedn, searchScope, searchFilter)#, searchAttribute)
    #ldap_result_id = l.search(basedn, searchScope, searchFilter)
    result_set = []
    while 1:
        result_type, result_data = l.result(ldap_result_id, 0)
        if (result_data == []):
            break
        else:
            ## if you are expecting multiple results you can append them
            ## otherwise you can just wait until the initial result and break out
            if result_type == ldap.RES_SEARCH_ENTRY:
                result_set.append(result_data)
    print (result_set)
except ldap.LDAPError as e:
    print (e)


try:
  res = l.delete("cn=mikkamakka,"+basedn)
  print("Delresult: "+str(l.result3(res)))
except ldap.LDAPError as e:
    print (e)

l.unbind_s()

