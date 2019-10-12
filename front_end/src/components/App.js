import React, {Component} from 'react';
import {BrowserRouter, Route} from 'react-router-dom';
import {Provider} from 'react-redux';
import axios from 'axios';
import {store} from '../redux/store';
import './App.scss';
import NavigationBar from './NavigationBar';
import DefaultPage from './pages/DefaultPage';
import MyCompetitions from './pages/MyCompetitions';

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
                  <Route path='/' render={(props) => <DefaultPage {...props}/>} exact/>
                  <Route path='/MyCompetitions' render={(props) => <MyCompetitions {...props}/>} exact/>
                </div>
              </Provider>
            </BrowserRouter>
        );
    }
}

