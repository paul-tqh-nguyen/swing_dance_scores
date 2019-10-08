import React, { Component } from 'react';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Button from '@material-ui/core/Button';
import './NavigationBar.scss';

class NavigationBar extends Component {
    render() {
        return (
              <AppBar position="fixed">
                <Toolbar className="navigation-bar-container">
                  <Button component={Link} to={'/'} color="inherit">Home</Button>
                  <Button component={Link} to={'/login'} color="inherit">Login</Button>
                  <Button component={Link} to={'/signup'} color="inherit">Sign Up</Button>
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
    //authenticated: state.user.authenticated
});

export default connect(mapStateToProps)(NavigationBar);
