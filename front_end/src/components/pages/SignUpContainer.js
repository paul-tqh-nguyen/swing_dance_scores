import React, {Component} from 'react';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import {bindActionCreators} from 'redux';
import {connect} from 'react-redux';
import {signUpUser} from '../../redux/actions';

class SignUpPage extends Component {
    constructor() {
        super();
        this.state = {
            email: '',
            password: '',
            confirmPassword: '',
            handle: '',
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
            confirmPassword: this.state.confirmPassword,
            handle: this.state.handle,
        };
        this.props.signUpUser(userData, this.props.history);
    };
    
    render() {
        // @todo make sure we do something useful with this ERRORS attribute of the state
        let emailTextField = <TextField
                                 id="email"
                                 name="email"
                                 type="email"
                                 label="Email"
        //helperText={errors.email} // have this display problems noted in teh redux store via NOTE_SIGNUP_PROBLEM
        //error={errors.email ? true : false} // have this display problems noted in teh redux store via NOTE_SIGNUP_PROBLEM
                                 value={this.state.email}
                                 onChange={this.handleChange}
                                 fullWidth
                             />;
        let passwordTextField = <TextField
                                           id="password"
                                                 name="password"
                                                 type="password"
                                                 label="Password"
        //helperText={errors.password} // have this display problems noted in teh redux store via NOTE_SIGNUP_PROBLEM
        //error={errors.password ? true : false} // have this display problems noted in teh redux store via NOTE_SIGNUP_PROBLEM
                                                 value={this.state.password}
                                                 onChange={this.handleChange}
                                                 fullWidth
                                       />;
        let confirmPasswordTextField = <TextField
                                           id="confirmPassword"
                                           name="confirmPassword"
                                           type="password"
                                           label="Confirm Password"
        //helperText={errors.password} // have this display problems noted in teh redux store via NOTE_SIGNUP_PROBLEM
        //error={errors.password ? true : false} // have this display problems noted in teh redux store via NOTE_SIGNUP_PROBLEM
                                           value={this.state.confirmPassword}
                                           onChange={this.handleChange}
                                           fullWidth
                                       />;
        let handleTextField = <TextField
                                 id="handle"
                                 name="handle"
                                 type="text"
                                 label="Handle"
        //helperText={errors.email} // have this display problems noted in teh redux store via NOTE_SIGNUP_PROBLEM
        //error={errors.email ? true : false} // have this display problems noted in teh redux store via NOTE_SIGNUP_PROBLEM
                                 value={this.state.handle}
                                 onChange={this.handleChange}
                                 fullWidth
                             />;
        let signUpButton = <Button
                               type="submit"
                               variant="contained"
                               color="primary"
        //disabled={loading} // @todo disable this when we're waiting for signup to complete
                           >
        Sign Up!
      </Button>;
        return (
            <div>
              <form noValidate onSubmit={this.handleSubmit}>
                {emailTextField}
                {passwordTextField}
                {confirmPasswordTextField}
                {handleTextField}
                {signUpButton}
              </form>
            </div>
        );
    }
}

const mapStateToProps = (state) => ({
});

const mapDispatchToProps = (dispatch) => {
    return bindActionCreators({signUpUser}, dispatch);
};

export default connect(mapStateToProps, mapDispatchToProps)(SignUpPage);
