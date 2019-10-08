import React, {Component} from 'react';
import {BrowserRouter, Route} from 'react-router-dom';
import {Provider} from 'react-redux';
import axios from 'axios';
import {store} from '../redux/store';
import './App.scss';
import HomePage from './HomePage';
import LoginPage from './LoginPage';
import SignUpPage from './SignUpPage';
import NavigationBar from './NavigationBar';

axios.defaults.baseURL = 'https://us-central1-swing-dance-scores.cloudfunctions.net/api';

export class App extends Component {
    componentDidMount() {
        let title = document.getElementsByTagName('title')[0];
        title.innerText = "Swing Dance Scores";
    }
    
    render() {
        // @todo use AuthRoute for something
        return (
            <BrowserRouter>
              <Provider store={store}>
                <NavigationBar/>
                <div className='center-frame-container'>
                  <Route path='/' render={(props) => <HomePage {...props}/>} exact/>
                  <Route path='/login' render={(props) => <LoginPage {...props}/>} exact/>
                  <Route path='/signup' render={(props) => <SignUpPage {...props}/>} exact/>
                </div>
              </Provider>
            </BrowserRouter>
        );
    }
}

