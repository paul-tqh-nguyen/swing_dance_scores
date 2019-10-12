import React, {Component} from 'react';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import {bindActionCreators} from 'redux';
import {connect} from 'react-redux';
import {loginUser} from '../../redux/actions';

class LoginContainer extends Component {
    constructor() {
        super();
        this.state = {
            email: '',
            password: '',
        };
    }

    handleChange = (event) => {
        this.setState({
            [event.target.name]: event.target.value
        });
    }
    
    handleSubmit = (event) => {
        event.preventDefault();
        const userData = {
            email: this.state.email,
            password: this.state.password,
        };
        this.props.loginUser(userData, this.props.history);
    };
    
    render() {
        // @todo make sure we do something useful with this ERRORS attribute of the state
        let emailTextField = <TextField
                                 id="email"
                                 name="email"
                                 type="email"
                                 label="Email"
                                 //helperText={errors.email} // have this display problems noted in the redux store via NOTE_LOGIN_PROBLEM
                                 //error={errors.email ? true : false} // have this display problems noted in teh redux store via NOTE_LOGIN_PROBLEM
                                 value={this.state.email}
                                 onChange={this.handleChange}
                                 fullWidth
                             />;
        let passwordTextField = <TextField
                                    id="password"
                                    name="password"
                                    type="password"
                                    label="Password"
                                    //helperText={errors.password} // have this display problems noted in teh redux store via NOTE_LOGIN_PROBLEM
                                    //error={errors.password ? true : false} // have this display problems noted in teh redux store via NOTE_LOGIN_PROBLEM
                                    value={this.state.password}
                                    onChange={this.handleChange}
                                    fullWidth
                                />;
        let loginButton = <Button
                              type="submit"
                              variant="contained"
                              color="primary"
        //disabled={loading} // @todo disable this when we're waiting for login to complete
                          >
                            Login
                          </Button>;
        return (
            <div>
              <form noValidate onSubmit={this.handleSubmit}>
                {emailTextField}
                {passwordTextField}
                {loginButton}
              </form>
            </div>
        );
    }
}

const mapStateToProps = (state) => ({
});

const mapDispatchToProps = (dispatch) => {
    return bindActionCreators({loginUser}, dispatch);
};

export default connect(mapStateToProps, mapDispatchToProps)(LoginContainer);
