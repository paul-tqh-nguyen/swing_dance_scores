
const { admin, db } = require("../util/admin");

const FBAuth = (request, response, next) => {
    let idToken;
    if (request.headers.authorization && request.headers.authorization.startsWith('Bearer ')) {
        idToken = request.headers.authorization.split('Bearer ')[1];
    } else {
        console.error(`No token found. ${request.headers.authorization}`);
        return response.status(403).json({ general: "Unauthorized action."});
    }
    admin.auth().verifyIdToken(idToken)
        .then(decodedToken => {
            request.user = decodedToken;
            return db.collection("users")
                .where("userId","==",request.user.uid)
                .limit(1)
                .get();
        })
        .then(data => {
            request.user.handle = data.docs[0].data().handle;
            return next();
        })
        .catch(err => {
            console.log("Error while evrifying token ", err);
            return response.status(403).json(err);
        });
    return null;
};

module.exports = { FBAuth };
