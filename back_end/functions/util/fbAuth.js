
const { admin, db } = require("../util/admin");

const FBAuthenticate = (request, response, next) => {
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
            console.error("Error while verifying token ", err);
            return response.status(403).json(err);
        });
    return null;
};

const possiblyFBAuthenticate = (request, response, next) => {
    let idToken;
    if (request.headers.authorization && request.headers.authorization.startsWith('Bearer ')) {
        idToken = request.headers.authorization.split('Bearer ')[1];
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
                console.error(err.message ? err.message : err.code);
                return next();
            });
    } else {
        return next();
    }
    return null;
};

module.exports = { FBAuthenticate, possiblyFBAuthenticate };
