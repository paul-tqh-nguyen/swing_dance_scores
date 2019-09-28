
const app = require('express')();
const { db } = require("./util/admin");
const { firebaseConfig } = require('./util/config.js');
const firebase = require('firebase');
firebase.initializeApp(firebaseConfig);

// Competitions
const { getAllCompetitions, postOneCompetition, findCompetition, deleteCompetition } = require('./handlers/competitions');
const { FBAuth } = require('./util/fbAuth');
// @todo refactor this to make sure all the routes make sense to us (the developers)
app.get('/competitions', getAllCompetitions);
app.post('/createCompetition', FBAuth, postOneCompetition);
app.get('/competition/:competitionId', findCompetition); // e.g. http://localhost:5000/swing-dance-scores/us-central1/api/competition/3QWUwBiPLFTwq4rlc1oo
app.delete('/competition/:competitionId', FBAuth, deleteCompetition); 
// @todo modify a competition

// Users
const { signup, login, uploadImage, addUserDetails, getUserData } = require('./handlers/users');
let token, userId;
app.post('/signup', signup);
app.post('/login', login);
app.post('/users/image', FBAuth, uploadImage);
app.post('/users/addUserDetails', FBAuth, addUserDetails);
app.get('/users/getUserDetails', FBAuth, getUserData);

const functions = require('firebase-functions');
exports.api = functions.https.onRequest(app);

exports.createNotificationOnCompetitionDelete = functions
    .firestore
    .document("competitions/{id}")
    .onDelete(snapshot => {
        db.doc(`/competitions/${snapshot.id}`)
            .get()
            .then(competitionDoc => {
                if (competitionDoc.exists) {
                    return db.doc(`/notifications/${snapshot.id}`).set({
                        competitionId: competitionDoc.id,
                        competitionName: competitionDoc.data().competitionName,
                        competitionCreatedAt: competitionDoc.data().createdAt,
                        competitionCreatorHandle: competitionDoc.data().creatorHandle,
                        createdAt: new Date().toISOString(),
                    });
                }
                return null;
            })
            .catch(err => {
                console.log(err);
                return null;
            });
    });
