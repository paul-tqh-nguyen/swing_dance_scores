
const app = require('express')();
const { db } = require("./util/admin");
const { firebaseConfig } = require('./util/config.js');
const firebase = require('firebase');
firebase.initializeApp(firebaseConfig);
const cors = require('cors');
app.use(cors());
const { FBAuthenticate, possiblyFBAuthenticate } = require('./util/fbAuth');

// Competitions
const { createCompetition, findCompetitionById, findCompetitionsModifiableByUser, findCompetitionsVisibleToUser, editCompetition, deleteCompetition, scoreCompetition } = require('./handlers/competitions');
// @todo refactor this to make sure all the routes make sense to us (the developers)
app.post('/createCompetition', FBAuthenticate, createCompetition);
app.get('/competition/:competitionId', possiblyFBAuthenticate, findCompetitionById); // e.g. http://localhost:5000/swing-dance-scores/us-central1/api/competition/3QWUwBiPLFTwq4rlc1oo
app.put('/competition/:competitionId', FBAuthenticate, editCompetition);
app.delete('/competition/:competitionId', FBAuthenticate, deleteCompetition); 
app.get('/modifiableCompetitions', FBAuthenticate, findCompetitionsModifiableByUser);
app.get('/visibleCompetitions', possiblyFBAuthenticate, findCompetitionsVisibleToUser);
app.put('/scoreCompetition/:competitionId', FBAuthenticate, scoreCompetition);
// Users
const { signup, login, uploadImage, addUserDetails, getUserData, updateUserData } = require('./handlers/users');
let token, userId;
app.post('/signup', signup);
app.post('/login', login);
app.post('/users/image', FBAuthenticate, uploadImage);
app.post('/users/addUserDetails', FBAuthenticate, addUserDetails);
app.get('/users/getUserDetails', FBAuthenticate, getUserData);
app.post('/users/updateUserDetails', FBAuthenticate, updateUserData);

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
                console.error(err);
                return null;
            });
    });
