import React, { Component } from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Button from '@material-ui/core/Button';
import './NavigationBar.scss';
import {logOut} from '../redux/actions';

class NavigationBar extends Component {
    render() {
        let { authenticated } = this.props;
        return (!authenticated) ? (null) : (
            <AppBar position="fixed">
              <Toolbar className="navigation-bar-container">
                <Button component={Link} to={'/MyCompetitions'} color="inherit">My Competitions</Button>
                <Button component={Link} to={'/MyProfile'} color="inherit">My Profile</Button>
                <Button component={Link} to={'/?loggedOutMostRecently=true'} onClick={this.props.logOut} color="inherit">Log Out</Button>
              </Toolbar>
            </AppBar>
        );
    }
}

//import PropTypes from 'prop-types';
// Navbar.propTypes = {
//   authenticated: PropTypes.bool.isRequired
// };

const mapStateToProps = (state) => ({
    authenticated: state.authenticated
});


const mapDispatchToProps = (dispatch) => {
    return bindActionCreators({logOut}, dispatch);
};

export default connect(mapStateToProps, mapDispatchToProps)(NavigationBar);
