import {
    NOTE_LOADING_STATUS_TRUE,
    NOTE_LOADING_STATUS_FALSE,
    NOTE_LOGIN_PROBLEM,
    FORGET_LOGIN_PROBLEMS,
    NOTE_USER_DATA_GATHERING_PROBLEM,
    FORGET_USER_DATA_GATHERING_PROBLEMS,
    NOTE_CURRENT_USER_INFO,
} from './types';
import {createStore, applyMiddleware, compose} from 'redux';
import thunk from 'redux-thunk';

const middleware = [thunk];

const initialState = {
    loading: false, // @todo do something with this
    loginErrors: [], // @todo do something with this ; make sure the previous errors are used or cleared
    userDataGatheringProblems: [], // @todo do something with this ; make sure the previous errors are used or cleared
    currentUserData: {}, // @todo do something with this
};

// @todo when this becomes big enough, abstract out these parts into helper reducers similar to what is done in this example:
// https://github.com/hidjou/classsed-react-firebase-client/tree/master/src/redux/reducers
function reducer(state=initialState, action) {
    switch (action.type) {
    case NOTE_LOADING_STATUS_TRUE:
        return {
            ...state, 
            loading: true,
        };
    case NOTE_LOADING_STATUS_FALSE:
        return {
            ...state, 
            loading: false,
        };
    case NOTE_LOGIN_PROBLEM:
        let currentLoginErrors = state.loginErrors;
        currentLoginErrors.push(action.loginError);
        return {
            ...state,
            loginErrors: currentLoginErrors,
        };
    case FORGET_LOGIN_PROBLEMS:
        return {
            ...state,
            loginErrors: [],
        };
    case NOTE_USER_DATA_GATHERING_PROBLEM:
        let updatedUserDataGatheringProblems = state.userDataGatheringProblems;
        updatedUserDataGatheringProblems.push(action.userDataGatheringProblem);
        return {
            ...state,
            userDataGatheringProblems: updatedUserDataGatheringProblems,
        };
    case FORGET_USER_DATA_GATHERING_PROBLEMS:
        return {
            ...state,
            userDataGatheringProblems: [],
        };
    case NOTE_CURRENT_USER_INFO:
        return {
            ...state,
            currentUserData: action.userData,
        };
    default:
        if (!action.type.includes("@@")) {
            console.log(`Unhandled redux action type ${action.type}`);
        }
        return state;
    }
}

const composeEnhancers = typeof window === 'object' && window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ ? window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__({}) : compose;
const enhancer = composeEnhancers(applyMiddleware(...middleware));

export const store = createStore(reducer, initialState, enhancer);

