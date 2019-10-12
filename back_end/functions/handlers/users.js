
const { firebaseConfig } = require('../util/config.js');
const firebase = require('firebase');
const { db, admin } = require("../util/admin");
const { signupValidationErrors, loginValidationErrors, reduceUserDetails } = require("../util/validators");

const noImageFileName = "no_image.png";

exports.signup = (request, response) => {
    const newUser = {
        email: request.body.email,
        password: request.body.password,
        confirmPassword: request.body.confirmPassword,
        handle: request.body.handle,
    };
    let errors = signupValidationErrors(newUser);
    if (Object.keys(errors).length>0) {
        return response.status(400).json(errors);
    }
    let userId, token;
    db.doc(`/users/${newUser.handle}`).get()
        .then(doc => {
            if (doc.exists) {
                return response.status(400).json({ handle: "This handle is already taken."});
            } else {
                return firebase.auth().createUserWithEmailAndPassword(newUser.email, newUser.password);
            }
        })
        .then(data => {
            userId = data.user.uid;
            return data.user.getIdToken();
        })
        .then(retrievedToken => {
            token = retrievedToken;
            const userCredentials = {
                handle: newUser.handle,
                email: newUser.email,
                createdAt: new Date().toISOString(),
                userId: userId,
                imageUrl: `https://firebasestorage.googleapis.com/v0/b/${firebaseConfig.storageBucket}/o/${noImageFileName}?alt=media`,
            };
            return db.doc(`/users/${newUser.handle}`).set(userCredentials);
        })
        .then(() => {
            return response.status(201).json({token: token});
        })
        .catch(err => {
            console.error(err);
            if (err.code === "auth/email-already-in-use") {
                return response.status(400).json({error: `The email address ${newUser.email} is already in use.`});
            } else {
                return response.status(500).json({error: err.code});
            }
        });
    return null;
};

const lastArrayElement = (array) => { // @todo move to helper file
    return array[array.length-1];
};

exports.login = (request, response) => {
    const user = {
        email: request.body.email,
        password: request.body.password,
    };
    let errors = loginValidationErrors(user);
    if (Object.keys(errors).length>0) {
        return response.status(400).json(errors);
    }
    let refreshToken;
    firebase.auth().signInWithEmailAndPassword(user.email, user.password)
        .then(data => {
            refreshToken = data.user.refreshToken;
            return data.user.getIdToken();
        })
        .then(token => {
            return response.json({token: token, refreshToken: refreshToken});
        })
        .catch(err => {
            console.error(err);
            if (err.code === "auth/wrong-password") {
                return response.status(403).json({ general: "Wrong credentials, please try again."});
            }
            return response.status(500).json({error: err.code});
        });
    return null;
};

exports.uploadImage = (request, response) => {
    const BusBoy = require('busboy');
    const path = require('path');
    const os = require('os');
    const fs = require('fs');
    const busboy = new BusBoy({ headers: request.headers });
    let imageFileName;
    let imageToBeUploaded = {};
    busboy.on('file', (fieldname, file, filename, encoding, mimetype) => {
        const imageExtension = lastArrayElement(filename.split('.'));
        if (mimetype !== 'image/jpeg') {
            return response.status(400).json({ error: 'Only JPEG images can be uploaded.' });
        }
        imageFileName = `${Date.now()}_${Math.floor(Math.random()*100000000000000)}.${imageExtension}`;
        console.log(`${imageFileName}`);
        const filepath = path.join(os.tmpdir(), imageFileName);
        imageToBeUploaded = {
            filepath: filepath,
            mimetype: mimetype,
        };
        file.pipe(fs.createWriteStream(filepath));
        return null;
    });
    busboy.on('finish', () => {
        admin.storage().bucket().upload(imageToBeUploaded.filepath, {
            resumable: false,
            metadata: {
                metadata: {
                    contentType: imageToBeUploaded.mimetype, 
                },
            },
        })
            .then(() => {
                const imageUrl = `https://firebasestorage.googleapis.com/v0/b/${firebaseConfig.storageBucket}/o/${imageFileName}?alt=media`;
                db.doc(`/users/${request.user.handle}`).update({ imageUrl: imageUrl});
                return imageUrl;
            })
            .then((imageUrl) => {
                return response.json({ message: "Image uploaded successfully.", imageUrl: imageUrl});
            })
            .catch((error) => {
                console.log(error);
                return response.status(500).json({error: error.code});
            });
    });
    busboy.end(request.rawBody);
};

exports.addUserDetails = (request, response) => {
    let userDetails = reduceUserDetails(request.body);
    db.doc(`/users/${request.user.handle}`).update(userDetails)
        .then(() => {
            // @todo is this status code right? should we use a put or update instead of a post for this?
            return response.status(200).json({message: "Details added successfully."});
        })
        .catch(err => {
            console.error(err);
            return response.status(500).json({ error: err.code });
        });
};

exports.getUserData = (request, response) => {
    db.collection("users")
        .where("handle", "==", request.user.handle)
        .limit(1)
        .get()
        .then(querySnapshot => {
            console.log(11);
            let docs = [];
            querySnapshot.forEach(doc => docs.push(doc));
            if (docs.length !== 1) {
                return response.status(500).json({ error: `Could not find user for handle ${request.user.handle}`});
            }
            let userData = docs[0].data();
            return response.json(userData);
        })
        .catch(err => {
            console.error(err);
            return response.status(500).json({ error: err.code });
        });
};

exports.deleteUser = (request, response) => {
    const user = {
        email: request.body.email,
        password: request.body.password,
    };
    let errors = loginValidationErrors(user);
    if (Object.keys(errors).length>0) {
        return response.status(400).json(errors);
    }
    firebase.auth().signInWithEmailAndPassword(user.email, user.password)
        .then(data => {
            let currentUser = firebase.auth().currentUser;
            return currentUser.delete();
        })
        .then(() => {
            // @todo is this status code right? should we use a put or update instead of a post for this?
            return response.status(200).json({message: "User deleted successfully."});
        })
        .catch(err => {
            console.error(err);
            if (err.code === "auth/wrong-password") {
                return response.status(403).json({ general: "Wrong credentials; cannot delete user."});
            }
            return response.status(500).json({error: err.code});
        });
    return null;
};
