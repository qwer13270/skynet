<template>
  <div style="height: 100vh; display: flex; align-items: center; justify-content: center; background-color: #0f9876">
    <div style="display: flex; background-color: white; width: 50%; border-radius: 5px; overflow: hidden">
      <div style="flex: 1">
        <img src="@/assets/login.png" alt="" style="width: 100%">
      </div>
      <div style="flex: 1; display: flex; align-items: center; justify-content: center">
        <el-form :model="user" style="width: 80%" :rules="rules" ref="loginRef">
          <div style="font-size: 20px; font-weight: bold; text-align: center; margin-bottom: 20px">Welcome UCS Satellite
            System
          </div>
          <el-form-item prop="username">
            <el-input prefix-icon="el-icon-user" size="medium" placeholder="Please Enter Username"
                      v-model="user.username"></el-input>
          </el-form-item>
          <el-form-item prop="password">
            <el-input prefix-icon="el-icon-lock" size="medium" show-password placeholder="Please Enter Password"
                      v-model="user.password"></el-input>
          </el-form-item>
          <el-form-item prop="code">
            <div style="display: flex">
              <el-input placeholder="Please Enter Valid Code" prefix-icon="el-icon-circle-check" size="medium"
                        style="flex: 1" v-model="user.code"></el-input>
              <div style="flex: 1; height: 36px">
                <valid-code @update:value="getCode"/>
              </div>
            </div>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" style="width: 100%" @click="login">Login</el-button>
          </el-form-item>
          <div style="display: flex">
            <div style="flex: 1">Don't have account? <span style="color: #0f9876; cursor: pointer"
                                                           @click="$router.push('/register')">Registration</span></div>
          </div>
        </el-form>
      </div>
    </div>

  </div>
</template>

<script>
import ValidCode from "@/components/ValidCode";
import axios from "axios";

export default {
  name: "Login",
  components: {
    ValidCode
  },
  data() {
    // Verification code verification
    const validateCode = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('Please Enter Valid Code'))
      } else if (value.toLowerCase() !== this.code) {
        callback(new Error('Valid Code Error'))
      } else {
        callback()
      }
    }

    return {
      code: '',  // The code passed by the verification code component
      user: {
        code: '',   // Code verification code entered by the user in the form
        username: '',
        password: ''
      },
      rules: {
        username: [
          {required: true, message: 'Please Enter Username', trigger: 'blur'},
        ],
        password: [
          {required: true, message: 'Please Enter Password', trigger: 'blur'},
        ],
        code: [
          {validator: validateCode, trigger: 'blur'}
        ],
      }
    }
  },
  created() {
    this.checkLogin();
  },
  methods: {
    getCode(code) {
      this.code = code.toLowerCase()
    },
    login() {
      axios.post('http://localhost:8000/api/login', this.user, {headers: {'Content-Type': 'application/json'}})
          .then(response => {
            console.log("Login response:", response.data);
            // Handle the token as per your requirement
            localStorage.setItem('authToken', response.data.token);
            localStorage.setItem('username', response.data.username);
            this.username = response.data.username; // Also set the username in the component's data
            this.$router.push('/'); // Redirect to homepage or dashboard
          })
          .catch(error => {
            this.error = error.response.data.error;
          })
    },
    checkLogin() {
      const token = localStorage.getItem('authToken');
      if (token) {
        const payload = JSON.parse(atob(token.split('.')[1])); // 解码JWT payload
        const today = new Date().toISOString().slice(0, 10);
        if (payload.login_date === today) {
          this.$router.push('/homepage');
        }
      }
    },
    logout() {
      localStorage.removeItem('authToken');
      this.$router.push('/login');
    }
  }
}
</script>

<style scoped>

</style>