import {
    NOTE_LOADING_STATUS_TRUE,
    NOTE_LOADING_STATUS_FALSE,
    NOTE_LOGIN_PROBLEM,
    FORGET_LOGIN_PROBLEMS,
    NOTE_USER_DATA_GATHERING_PROBLEM,
    FORGET_USER_DATA_GATHERING_PROBLEMS,
    NOTE_CURRENT_USER_INFO,
    FORGET_SIGNUP_PROBLEMS,
    NOTE_SIGNUP_PROBLEM,
    NOTE_AUTHENTICATION_TRUE,
    NOTE_AUTHENTICATION_FALSE, 
} from './types';
import axios from 'axios';

const setAuthorizationHeader = (token, refreshToken) => {
    const FBIdToken = `Bearer ${token}`;
    localStorage.setItem('FBIdToken', FBIdToken);
    localStorage.setItem('FBRefreshToken', refreshToken);
    axios.defaults.headers.common['Authorization'] = FBIdToken;
};

const getUserData = () => (dispatch) => {
    dispatch({ type: NOTE_LOADING_STATUS_TRUE });
    axios
        .get('/users/getUserDetails')
        .then((response) => {
            dispatch({
                type: NOTE_CURRENT_USER_INFO,
                userData: response.data
            });
            dispatch({ type: FORGET_USER_DATA_GATHERING_PROBLEMS });
        })
        .catch((err) => {
            console.error(err);
            dispatch({
                type: NOTE_USER_DATA_GATHERING_PROBLEM,
                userDataGatheringProblem: err
            });
        });
    dispatch({ type: NOTE_LOADING_STATUS_FALSE });
};

export const loginUser = (userData, history) => (dispatch) => {
    dispatch({ type: NOTE_LOADING_STATUS_TRUE });
    axios
        .post('/login', userData)
        .then((response) => {
            setAuthorizationHeader(response.data.token, response.data.refreshToken);
            getUserData()(dispatch);
            dispatch({ type: FORGET_LOGIN_PROBLEMS });
            dispatch({ type: NOTE_AUTHENTICATION_TRUE });
            history.push('/MyCompetitions');
        })
        .catch((err) => {
            // @todo handle certain cases like bad credentials
            console.error(err.response.data);
            dispatch({ type: NOTE_AUTHENTICATION_FALSE });
            dispatch({
                type: NOTE_LOGIN_PROBLEM,
                loginError: err.response.data,
            });
        });
    dispatch({ type: NOTE_LOADING_STATUS_FALSE });
};

export const signUpUser = (userData, history) => (dispatch) => {
    dispatch({ type: NOTE_LOADING_STATUS_TRUE }); // @todo add some animations while we are loading
    axios
        .post('/signup', userData)
        .then((response) => {
            setAuthorizationHeader(response.data.token, response.data.refreshToken);
            getUserData()(dispatch);
            dispatch({ type: FORGET_SIGNUP_PROBLEMS });
            history.push('/MyCompetitions');
        })
        .catch((err) => {
            // @todo handle certain cases like bad credentials
            console.error(err.response.data);
            dispatch({ type: NOTE_AUTHENTICATION_FALSE });
            dispatch({
                type: NOTE_SIGNUP_PROBLEM, // @todo test bad sign up issues
                loginError: err.response.data,
            });
        });
    dispatch({ type: NOTE_LOADING_STATUS_FALSE });
};

export const logOut = () => (dispatch) => {
    setAuthorizationHeader("", "");
    dispatch({ type: NOTE_LOADING_STATUS_TRUE });
    dispatch({ type: FORGET_LOGIN_PROBLEMS });
    dispatch({ type: NOTE_AUTHENTICATION_FALSE });
    dispatch({ type: FORGET_USER_DATA_GATHERING_PROBLEMS });
    dispatch({ type: FORGET_SIGNUP_PROBLEMS });
    dispatch({ type: NOTE_LOADING_STATUS_FALSE });
};
