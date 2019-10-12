import React, {Component} from 'react';
import {bindActionCreators} from 'redux';
import {connect} from 'react-redux';
import './DefaultPage.scss';
import LoginContainer from './LoginContainer';
import SignUpContainer from './SignUpContainer';
import {getUrlParameter} from '../../util/miscUtilities';

class DefaultPage extends Component {
    render() {
        const loggedOutMostRecently = getUrlParameter("loggedOutMostRecently");
        if (loggedOutMostRecently) {
            console.log("We just logged out."); // @todo make something pop up for this
        }
        return (
            <div>
              <LoginContainer {...this.props}/>
              <SignUpContainer {...this.props}/>
            </div>
        );
    }
}

export default DefaultPage;
