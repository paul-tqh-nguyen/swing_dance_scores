
const {db} = require("../util/admin");

exports.getAllCompetitions = (request, response) => {
    db.collection('competitions')
        .orderBy("createdAt", "desc")
        .get()
        .then((data) => {
            let competitions = [];
            data.forEach(doc => {
                competitions.push({
                    competitionId: doc.id,
                    competitionName: doc.data().competitionName,
                    createdAt: doc.data().createdAt,
                    creatorHandle: doc.data().creatorHandle,
                });
            });
            return response.json(competitions);
        })
        .catch((errorMessage) => console.error(errorMessage));
};

exports.postOneCompetition = (request, response) => {
    const newCompetition = {
        competitionName: request.body.competitionName,
        createdAt: new Date().toISOString(),
        creatorHandle: request.user.handle,
    };
    db.collection('competitions')
        .add(newCompetition)
        .then((doc) => {
            return response.status(201).json({message: `Document ${doc.id} created successfully.`});
        })
        .catch((errorMessage) => {
            return response.status(500).json({error: `We hit an error! ${errorMessage}`});
        });
};

exports.findCompetition = (request, response) => {
    let competitionData = {};
    db.doc(`/competitions/${request.params.competitionId}`).get()
        .then(doc => {
            if (!doc.exists) {
                return response.status(404).json({ error: `Competition information for competition ID ${request.params.competitionId} not found.`});
            }
            competitionData = doc.data();
            return response.json(competitionData);
        })
        .catch(err => {
            console.error(err);
            return response.status(500).json({error: err.code});
        });
};

const competitionModificationAuthenticationCheck = (request, response, next) => {
    const competitionDocument = db.doc(`/competitions/${request.params.competitionId}`);
};

exports.deleteCompetition = (request, response) => { // @todo make this api signature consisten with the others and have all params in the body
    const competitionDocument = db.doc(`/competitions/${request.params.competitionId}`);    competitionDocument.get()
        .then(doc => {
            if (!doc.exists) {
                return response.status(404).json({ error: `Could not delete competition with ID ${request.params.competitionId} as no competition with that ID was found.`});
            } else if (doc.data().creatorHandle !== request.user.handle) {
                return response.status(403).json({ error: `${request.user.handle} is not authorized to delete the competition with ID ${request.params.competitionId}.`});
            } else { 
                competitionDocument.delete();
                return response.status(204).json({message: `Competition with ID ${request.params.competitionId} deleted.`});
            }
        })
        .catch(err => {
            console.error(err);
            return response.status(500).json({error: err.code});
        });
};
