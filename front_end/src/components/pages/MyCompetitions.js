import React, {Component} from 'react';
import {bindActionCreators} from 'redux';
import {connect} from 'react-redux';
import {loginUser} from '../../redux/actions';

class MyCompetitions extends Component {
    constructor() {
        super();
        this.state = {
            // @todo contain the users and all their competitions
        };
    }
    
    render() {
        let { authenticated, history } = this.props;
        if (!authenticated) {
            // @todo this makes us login again after a refresh 
            history.push('/');
        }
        return (
            <div>
              @todo put something here ; we've hit the MyCompetitions page, which means we're authenticated.
            </div>
        );
    }
}

const mapStateToProps = (state) => ({
    authenticated: state.authenticated
});

export default connect(mapStateToProps)(MyCompetitions);
