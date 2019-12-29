const { createCompetitionValidationErrors, editCompetitionValidationErrors, allCompetitionInfoKeysModifiableByUser } = require("../util/validators");
const { db } = require("../util/admin");

exports.createCompetition = (request, response) => {
    let validationErrors = createCompetitionValidationErrors(request.body);
    if (Object.keys(validationErrors).length > 0) {
        return response.status(400).json(validationErrors);
    } else if (!request.body.usersWithModificationPrivileges.includes(request.user.handle)) {
        return response.status(500).json({error: `All competition creation requests must have it so that the competition can be modified by the user creating the competition.`});
    }
    const newCompetition = {
        createdAt: new Date().toISOString(),
        lastModifiedAt: new Date().toISOString(),
        competitionName: request.body.competitionName,
        category: request.body.category,
        judges: request.body.judges,
        competitorInfo: request.body.competitorInfo,
        usersWithModificationPrivileges: request.body.usersWithModificationPrivileges,
        privacy: request.body.privacy,
        creatorHandle: request.user.handle, 
    };
    let newCompetitionId;
    return db.collection('unscoredCompetitions')
        .add(newCompetition)
        .then((doc) => {
            newCompetitionId = doc.id;
            let userDocPromises = request.body.usersWithModificationPrivileges.map((handle) => db.doc(`/users/${handle}`).get());
            return Promise.all(userDocPromises);
        })
        .then(docs => {
            let userUpdatePromises = docs.map(doc => {
                if (!doc.exists) {
                    throw new Error(`${request.body.usersWithModificationPrivileges} contains an invalid user handle.`);
                }
                let userData = doc.data();
                let newModifiableCompetitionIds = userData.modifiableCompetitionIds;
                newModifiableCompetitionIds.push(newCompetitionId);
                let updatedUserData = Object.assign({}, userData, {modifiableCompetitionIds: newModifiableCompetitionIds});
                let handle = doc.id;
                return db.doc(`/users/${handle}`).set(updatedUserData);
            });
            return userUpdatePromises;
        }).then(()=>{
            return response.status(201).json({
                message: `Competition ${newCompetitionId} created successfully.`,
                competitionId: newCompetitionId
            });
        })    
        .catch((error) => {
            console.error(error);
            return response.status(500).json({error: `We hit an error while creating the competition! ${(error.message ? error.message : error.code)}`});
        });
};

exports.findCompetitionById = (request, response) => {
    return db.doc(`/unscoredCompetitions/${request.params.competitionId}`).get()
        .then(doc => {
            if (!doc.exists) {
                return response.status(404).json({ error: `Competition information for competition ID ${request.params.competitionId} not found.`});
            }
            let competitionData = doc.data();
            if (competitionData.privacy !== "public") {
                if (!request.user || !request.user.handle) {
                    throw new Error(`Authentication required to view competition ${request.params.competitionId}.`);
                } else if (!competitionData.usersWithModificationPrivileges.includes(request.user.handle)) {
                    throw new Error(`${request.user.handle} cannot modify competition ${request.params.competitionId}.`);
                }
            }
            return response.status(200).json(competitionData);
        })
        .catch(err => {
            console.error(err);
            return response.status(500).json({error: (err.message ? err.message : err.code) });
        });
};

const competitionIdsModifiableByUserWithHandle = (handle) => {
    return db.doc(`/users/${handle}`)
        .get()
        .then(doc => {
            if (!doc.exists) {
                throw new Error(`${handle} is not a valid handle.`);
            }
            let userData = doc.data();
            let competitionIds = userData.modifiableCompetitionIds;
            return competitionIds;
        });
};

const competitionInfoForCompetitionId = (competitionId) => {
    return db.doc(`/unscoredCompetitions/${competitionId}`).get()
        .then(doc => {
            if (!doc.exists) {
                throw new Error(`Competition information for competition ID ${competitionId} not found.`);
            }
            let competitionInfo = {competitionId: competitionId}; 
            competitionInfo = Object.assign({}, doc.data(), competitionInfo);
            return competitionInfo;
        });
};

const firstAmong = (array, test) => { // @todo move to utilities file
    test = test || (x => x) ;
    for(var index = 0 ; index < array.length; index++) {
        let testedValue = test(array[index]);
        if (testedValue) {
            return testedValue;
        }
    }
    return null;
};

const modifiableCompetitionInfosForUserWithHandle = (handle) => {
    return competitionIdsModifiableByUserWithHandle(handle)
        .then(competitionIds => {
            let competitionInfoPromises = competitionIds.map(competitionInfoForCompetitionId);
            return Promise.all(competitionInfoPromises);
        });
};

exports.findCompetitionsModifiableByUser = (request, response) => {
    let handle = "user" in request && "handle" in request.user ? request.user.handle : null;
    return modifiableCompetitionInfosForUserWithHandle(handle)
        .then(competitionInfos => {
            return response.status(200).json(competitionInfos);
        })
        .catch(error => {
            console.error(error);
            return response.status(500).json({error: (error.message ? error.message : error.code)});
        });
};

const publicCompetitionInfos = () => {
    let publicCompetitionInfosPromise = db.collection('unscoredCompetitions')
        .where("privacy","==","public")
        .get()
        .then(data => {
            let docs = data.docs;
            let publicCompetitionInfos = docs.map(doc => {
                return Object.assign({}, doc.data(), {competitionId: doc.id});
            });
            return publicCompetitionInfos;
        });
    return publicCompetitionInfosPromise;
};

exports.findCompetitionsVisibleToUser = (request, response) => {
    let handle = ("user" in request && "handle" in request.user) ? request.user.handle : null;
    let modifiableCompetitionInfosPromise = handle ? modifiableCompetitionInfosForUserWithHandle(handle) : Promise.all([]);
    let publicCompetitionInfosPromise = publicCompetitionInfos();
    return Promise.all([publicCompetitionInfosPromise, modifiableCompetitionInfosPromise])
        .then(publicCompetitionInfosAndModifiableCompetitionInfos => {
            let publicCompetitionInfos, modifiableCompetitionInfos; 
            [ publicCompetitionInfos, modifiableCompetitionInfos] = publicCompetitionInfosAndModifiableCompetitionInfos;
            let visibleCompetitionInfos = publicCompetitionInfos.concat(modifiableCompetitionInfos);
            return response.status(200).json(visibleCompetitionInfos);
        })
        .catch(error => {
            console.error(error);
            return response.status(500).json({error: (error.message ? error.message : error.code)});
        });
};

exports.editCompetition = (request, response) => { // @todo add a test that makes sure the user is one of the valid users who can modify the competition
    let competitionId = request.params.competitionId;
    let newCompetitionInfo = request.body;
    let validationErrors = editCompetitionValidationErrors(competitionId, newCompetitionInfo);
    if (Object.keys(validationErrors).length > 0) {
        return response.status(400).json(validationErrors);
    }
    let updatedCompetitionInfo = { lastModifiedAt: new Date().toISOString() };
    allCompetitionInfoKeysModifiableByUser.forEach(key => {
        if (key in newCompetitionInfo) {
            updatedCompetitionInfo[key] = newCompetitionInfo[key];
        }
    });
    return db.doc(`/unscoredCompetitions/${competitionId}`)
        .update(updatedCompetitionInfo)
        .then(()=>{
            return response.status(200).json({message: `Competition ${competitionId} updated successfully.`}); // @todo figure out if there's a better status code
        })    
        .catch((error) => {
            let humanReadableErrorString = `We hit an error while editing competition ${competitionId}! ${(error.message ? error.message : error.code)}`;
            console.error(humanReadableErrorString);
            console.error(error);
            return response.status(500).json({error: humanReadableErrorString});
        });
};

exports.deleteCompetition = (request, response) => { // @todo make this api signature consistent with the others and have all params in the body
    let competitionIdToRemove = request.params.competitionId;
    return db.doc(`/unscoredCompetitions/${competitionIdToRemove}`)
        .get()
        .then(doc => {
            if (!doc.exists) {
                return response.status(404).json({ error: `Could not delete competition with ID ${competitionIdToRemove} as no competition with that ID was found.`});
            } else if (!doc.data().usersWithModificationPrivileges.includes(request.user.handle)) {
                return response.status(403).json({ error: `${request.user.handle} is not authorized to delete the competition with ID ${competitionIdToRemove}.`});
            } else { 
                return db.doc(`/unscoredCompetitions/${competitionIdToRemove}`).delete();
            }
        })
        .then(() => {
            return db.collection('users')
                .where('modifiableCompetitionIds','array-contains',competitionIdToRemove)
                .get();
        })
        .then(data => {
            let docs = data.docs;
            let promisesToUpdateModifiableCompetitionIdsOfUsers = docs.map(doc => {
                let oldModifiableCompetitionIds = doc.data().modifiableCompetitionIds;
                let newModifiableCompetitionIds = oldModifiableCompetitionIds.filter(competitionId => (competitionIdToRemove !== competitionId));
                let handle = doc.id;
                return db.doc(`/users/${handle}`).update({modifiableCompetitionIds: newModifiableCompetitionIds});
            });
            return Promise.all(promisesToUpdateModifiableCompetitionIdsOfUsers);
        })
        .then(() => {
            return response.status(200).json({message: `Competition with ID ${competitionIdToRemove} deleted.`}); // @todo is this the right status code?
        })
        .catch(err => {
            console.error(err);
            return response.status(500).json({error: err.code});
        });
};

const histogramFromArray = array => { // @todo move to a utilities file
    let histogram = {};
    array.forEach(elem => {
        if (!histogram[elem]) {
            histogram[elem] = 1;
        } else {
            histogram[elem]++;
        }
    });
    return histogram;
};

const majorityScore = competitorJudgeScoreData => {
    let numberOfJudges = competitorJudgeScoreData.length;
    let threshholdForMajority = Math.ceil((numberOfJudges+1)/2);
    let scoreNumbers = competitorJudgeScoreData.map(scoreDatum => scoreDatum['judgeScore']);
    let scoreNumbersHistogram = histogramFromArray(scoreNumbers);
    let majorityScore;
    for (var score in scoreNumbersHistogram) {
        if (!majorityScore) {
            let scoreCount = scoreNumbersHistogram[score];
            if (scoreCount >= threshholdForMajority) {
                majorityScore = score;
            }
        }
    }
    return majorityScore;
};

const competitorJudgeScoreDataCountRank = (competitorJudgeScoreData, rank) => competitorJudgeScoreData.map(scoreDatum => scoreDatum['judgeScore']).filter(judgeScore => judgeScore === rank);
const competitorJudgeScoreDataCountOnes = competitorJudgeScoreData => competitorJudgeScoreDataCountRank(competitorJudgeScoreData, 1);
const competitorJudgeScoreDataCountTwos = competitorJudgeScoreData => competitorJudgeScoreDataCountRank(competitorJudgeScoreData, 2);

const prelimsScoreIsHigher = (scoreA, scoreB) => {
    let scoreAMajorityScore = majorityScore(scoreA);
    let scoreBMajorityScore = majorityScore(scoreB);
    if (scoreAMajorityScore!==scoreBMajorityScore) {
        return scoreAMajorityScore > scoreBMajorityScore;
    }
    // @todo verify that these tie breakers are legit
    let scoreAOnesCount = competitorJudgeScoreDataCountOnes(scoreA);
    let scoreBOnesCount = competitorJudgeScoreDataCountOnes(scoreB);
    if (scoreAOnesCount !== scoreBOnesCount) {
        return scoreAOnesCount > scoreBOnesCount;
    }
    let scoreATwosCount = competitorJudgeScoreDataCountTwos(scoreA);
    let scoreBTwosCount = competitorJudgeScoreDataCountTwos(scoreB);
    if (scoreATwosCount !== scoreBTwosCount) {
        return scoreATwosCount > scoreBTwosCount;
    }
    return false;
};

const sortedCompetitorsWithPlacementsForPrelims = (competitorInfo) => {
    let sortedCompetitorsWithPlacements = [];
    let numberOfCompetitors = competitorInfo.length;
    let sortedCompetitors = competitorInfo.sort(prelimsScoreIsHigher);
    let placement = 1;
    for (var competitorIndex = 0 ; competitorIndex < numberOfCompetitors-1 ; competitorIndex++) {
        let currentCompetitor = sortedCompetitors[competitorIndex];
        let nextCompetitor = sortedCompetitors[competitorIndex];
        let competitorWithPlacement = Object.assign(currentCompetitor, {placement: placement});
        sortedCompetitorsWithPlacements.push(competitorWithPlacement);
        let currentAndNextCompetitorAreTied = !prelimsScoreIsHigher(currentCompetitor, nextCompetitor) && !prelimsScoreIsHigher(nextCompetitor, currentCompetitor);
        if (!currentAndNextCompetitorAreTied) {
            placement++;
        }
    }
    return sortedCompetitorsWithPlacements;
};

const sortedCompetitorsWithPlacementsForFinals = (competitorInfo, judges) => {
    let numberOfCompetitors = competitorInfo.length;
    let sortedCompetitorsWithPlacements = [];
    let headJudge = judges[0]; // @todo this is a stub, head judge score should be a last resort
    let headJudgePrefersScore = (scoreA, scoreB) => {
        let scoreAHeadJudgeScore = scoreA.filter(scoreDatum => scoreDatum['judge']===headJudge)[0]['judgeScore'];
        let scoreBHeadJudgeScore = scoreB.filter(scoreDatum => scoreDatum['judge']===headJudge)[0]['judgeScore'];
        return scoreAHeadJudgeScore<scoreBHeadJudgeScore;
    };
    let currentPlacement = 1;
    let remainingCompetitorScores = competitorInfo;
    let updatedRemainingCompetitorScores;
    let competitorHasScoredHighEnoughForCurrentPlacement = competitorScoreData => {
        let competitorScoresFromJudges = competitorScoreData.map(scoreDatum => scoreDatum['judgeScore']);
        let numberOfScoresFromJudgesCompetitorGotThatQualifyForCurrentPlacement = competitorScoresFromJudges.filter(scoreFromJudge => (scoreFromJudge <= currentPlacement)).length;
        let competitorHasScoredHighEnoughForCurrentPlacement = (numberOfScoresFromJudgesCompetitorGotThatQualifyForCurrentPlacement >= threshholdForMajority);
        if (!competitorHasScoredHighEnoughForCurrentPlacement) {
            updatedRemainingCompetitorScores.push(competitorScoreData);
        }
        return competitorHasScoredHighEnoughForCurrentPlacement;
    };
    let currentReleventScoreThreshold = 1;
    let threshholdForMajority = Math.ceil((judges.length+1)/2);
    for (var placementCalculationIterationIndex = 0; placementCalculationIterationIndex < numberOfCompetitors && currentPlacement <= numberOfCompetitors; placementCalculationIterationIndex++) {
        updatedRemainingCompetitorScores = [];
        let bestCompetitorScoresforCurrentPlacement = remainingCompetitorScores.filter(competitorHasScoredHighEnoughForCurrentPlacement);
        remainingCompetitorScores = updatedRemainingCompetitorScores;
        bestCompetitorScoresforCurrentPlacement = bestCompetitorScoresforCurrentPlacement.sort(headJudgePrefersScore);
        for (var bestCompetitorScoreIndex = 0; bestCompetitorScoreIndex<bestCompetitorScoresforCurrentPlacement.length; bestCompetitorScoreIndex++) {
            let bestCompetitorScore = bestCompetitorScoresforCurrentPlacement[bestCompetitorScoreIndex];
            let bestCompetitorScoreWithPlacement = Object.assign(bestCompetitorScore, {placement: currentPlacement});
            sortedCompetitorsWithPlacements.push(bestCompetitorScoreWithPlacement);
            currentPlacement++;
        }
    }
    return sortedCompetitorsWithPlacements;
};

const scoreCompetitionFromUnscoredCompetitionData = (unscoredCompetitionData) => {
    let { category, competitorInfo, judges } = unscoredCompetitionData;
    let sortedCompetitorsWithPlacements;
    if (category === "prelims") {
        sortedCompetitorsWithPlacements = sortedCompetitorsWithPlacementsForPrelims(competitorInfo);
    } else if (category === "finals") {
        sortedCompetitorsWithPlacements = sortedCompetitorsWithPlacementsForFinals(competitorInfo, judges);
    } else {
        throw new Error(`Competition category data is invalid.`);
    }
    let scoredCompetitionData = {
        createdAt: new Date().toISOString(),
        category: category,
        sortedCompetitorsWithPlacements: sortedCompetitorsWithPlacements,
    };
    return scoredCompetitionData;
};

exports.scoreCompetition = (request, response) => { // @todo all the helpers of this function need better variable names
    let handle = request.user.handle;
    let competitionId = request.params.competitionId;
    let unscoredCompetitionData;
    return db.doc(`/unscoredCompetitions/${competitionId}`)
        .get()
        .then(doc => {
            if (!doc.exists) {
                return response.status(404).json({ error: `Could not find competition with ID ${competitionId}.`});
            }
            unscoredCompetitionData = doc.data();
            if (!unscoredCompetitionData.usersWithModificationPrivileges.includes(request.user.handle)) {
                return response.status(403).json({ error: `${request.user.handle} is not authorized to score the competition with ID ${competitionId}.`});
            } else { 
                return db.collection('scoringPrivileges')
                    .where('handle','==',handle)
                    .get();
            }
        })
        .then(data => {
            let scoringPrivilegeDocs = data.docs;
            let scoringIsAuthorized = scoringPrivilegeDocs.filter(scoringPrivilegeDoc => {
                let { startDateISOString, endDateISOString } = scoringPrivilegeDoc.data();
                let startDate = Date.parse(startDateISOString);
                let endDate = Date.parse(endDateISOString);
                let currentDate = new Date();
                let scoringPrivilegeSpansCurrentDate = (startDate < currentDate) && (currentDate < endDate);
                return scoringPrivilegeSpansCurrentDate;
            });
            if (!scoringIsAuthorized) {
                throw new Error(`Scoring for ${handle} is not currently authorized.`);
            }
            return db.doc(`/scoredCompetitions/${competitionId}`).get();
        })
        .then(doc => {
            if (doc.exists) {
                let alreadyExistingScoredData = doc.data();
                return response.status(200).json(alreadyExistingScoredData);
            } else {
                let newlyScoredCompetitionData = scoreCompetitionFromUnscoredCompetitionData(unscoredCompetitionData);
                return response.status(200).json(newlyScoredCompetitionData);
            }
        })
        .catch(err => {
            console.error(err);
            return response.status(500).json({error: err.code});
        });
};
