import styles from "../styles/Form.module.css"
import { useState } from "react"
import api from "../api"
import { useNavigate, Link } from "react-router-dom"

function Register() {
    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")
    const [email, setEmail] = useState("")
    const [confirmPassword, setConfirmPassword] = useState("")
    const navigate = useNavigate()

    const handleSubmit = async (e) => {
        e.preventDefault()
        try {
            await api.post("/users/register/", { username, password, email }, {withCredentials: true})
            navigate("/")
        } catch (error) {
            if (error.response) {
                if (error.response.data.username) {
                    alert("Username error: " + error.response.data.username[0])
                }
                if (error.response.data.password) {
                    alert("Password error: " + error.response.data.password[0]) 
                }
                if (error.response.data.email) {
                    alert("Email error: " + error.response.data.email[0])
                }
                console.error("Response status:", error.response.status)
            } else if (error.request) {
                console.error("Request error:", error.request)
                alert("No response received from server")
            } else {
                console.error("Error message:", error.message)
                alert(error.message)
            }
        }
    }

    return (
        <div className={styles.body}>
            <div className={styles.form}>
                <div className={styles.container}>
                    <div className={styles.loginSection}>
                        <div className={styles.loginHeader}>
                            <h1>REGISTER</h1>
                        </div>
                        <form id="login-form" onSubmit={handleSubmit}>
                            <div className={styles.formGroup}>
                                <label htmlFor="username">User name</label>
                                <input 
                                    type="text" 
                                    id="username" 
                                    name="username"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    required
                                />
                            </div>
                            <div className={styles.formGroup}>
                                <label htmlFor="email">Email</label>
                                <input 
                                    type="email" 
                                    id="email" 
                                    name="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />
                            </div>
                            <div className={styles.formGroup}>
                                <label htmlFor="password">Password</label>
                                <input 
                                    type="password" 
                                    id="password" 
                                    name="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />
                            </div>
                            <div className={styles.formGroup}>
                                <label htmlFor="confirmPassword">Repeat Password</label>
                                <input 
                                    type="password" 
                                    id="confirmPassword" 
                                    name="confirmPassword"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    required
                                />
                            </div>
                            <button type="submit" className={styles.submitBtn}>SUBMIT</button>
                        </form>
                        <div className={styles.createAccount}>
                            <Link to="/login">Log in Account</Link>
                        </div>
                        <div className={styles.alternativeLogin}>
                            <p>Or</p>
                            <div className={styles.socialLogin}>
                                <div className={styles.socialBtn}>
                                    <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M12.545,10.239v3.821h5.445c-0.712,2.315-2.647,3.972-5.445,3.972c-3.332,0-6.033-2.701-6.033-6.032s2.701-6.032,6.033-6.032c1.498,0,2.866,0.549,3.921,1.453l2.814-2.814C17.503,2.988,15.139,2,12.545,2C7.021,2,2.543,6.477,2.543,12s4.478,10,10.002,10c8.396,0,10.249-7.85,9.426-11.748L12.545,10.239z' fill='%234285F4'/%3E%3C/svg%3E" alt="Google login" />
                                </div>
                                <div className={styles.socialBtn}>
                                    <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M12,2C6.477,2,2,6.477,2,12c0,5.013,3.693,9.153,8.505,9.876V14.65H8.031v-2.629h2.474v-1.749 c0-2.896,1.411-4.167,3.818-4.167c1.153,0,1.762,0.085,2.051,0.124v2.294h-1.642c-1.022,0-1.379,0.969-1.379,2.061v1.437h2.995 l-0.406,2.629h-2.588v7.226C18.307,21.153,22,17.013,22,12C22,6.477,17.523,2,12,2z' fill='%231877F2'/%3E%3C/svg%3E" alt="Facebook login" />
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className={styles.imageSection}>
                        <img src="https://static.tildacdn.com/stor3264-6539-4332-b765-346164306437/39579332.jpg" alt="African woman in headwrap" />
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Register