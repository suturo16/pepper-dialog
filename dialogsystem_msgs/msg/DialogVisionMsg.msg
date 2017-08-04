#dialogmanagement-facerecognition-general format for information interchange

#type indicates whether it is a query or return value are query,return.
#commandName indicates the name of the query or the name of the query provoking the return
#userName indicates the eventual user's name the message might be about
#userId indicates the eventual user's Id the message might be about
#accuracy indicates the recognition accuracy of the eventual user the message is about

string typ
string commandName
string userName
string userId
string accuracy
