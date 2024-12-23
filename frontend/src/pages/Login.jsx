import styles from "../styles/Form.module.css"
import { useState } from "react"
import api from "../api"
import { useNavigate, Link } from "react-router-dom"

function Login() {
    const [username, setUsername] = useState("")
    const [password, setPassword] = useState("")
    const [showPassword, setShowPassword] = useState(false)
    const navigate = useNavigate()

    const handleSubmit = async (e) => {
        e.preventDefault()
        try {
            await api.post("/users/login/", { username, password }, {withCredentials: true})
            navigate("/")
        } catch (error) {
            alert(error)
        }
    }

    const togglePassword = () => {
        setShowPassword(!showPassword)
    }

    return (
        <div className={styles.body}>
            <div className={styles.form}>
                <div className={styles.container}>
                    <div className={styles.imageSection}>
                        <img src="https://static.tildacdn.com/stor3238-6634-4332-a461-353137663739/48396303.jpg" alt="Some stylish woman" />
                    </div>
                    <div className={styles.loginSection}>
                        <div className={styles.loginHeader}>
                            <h1>LOG IN</h1>
                        </div>
                        <form id="login-form" onSubmit={handleSubmit}>
                            <div className={styles.formGroup}>
                                <label htmlFor="username">Username | E-mail</label>
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
                                <label htmlFor="password">Password</label>
                                <input 
                                    type={showPassword ? "text" : "password"}
                                    id="password" 
                                    name="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />
                                <button 
                                    type="button" 
                                    id="login-toggle-password" 
                                    className={styles.togglePassword}
                                    onClick={togglePassword}
                                >
                                    {showPassword ? (
                                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" color="#999999" fill="none">
                                            <path d="M22 8C22 8 18 14 12 14C6 14 2 8 2 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                                            <path d="M15 13.5L16.5 16" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                                            <path d="M20 11L22 13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                                            <path d="M2 13L4 11" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                                            <path d="M9 13.5L7.5 16" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                                        </svg>
                                    ) : (
                                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" color="#999999" fill="none">
                                            <path d="M21.544 11.045C21.848 11.4713 22 11.6845 22 12C22 12.3155 21.848 12.5287 21.544 12.955C20.1779 14.8706 16.6892 19 12 19C7.31078 19 3.8221 14.8706 2.45604 12.955C2.15201 12.5287 2 12.3155 2 12C2 11.6845 2.15201 11.4713 2.45604 11.045C3.8221 9.12944 7.31078 5 12 5C16.6892 5 20.1779 9.12944 21.544 11.045Z" stroke="currentColor" strokeWidth="1.5" />
                                            <path d="M15 12C15 10.3431 13.6569 9 12 9C10.3431 9 9 10.3431 9 12C9 13.6569 10.3431 15 12 15C13.6569 15 15 13.6569 15 12Z" stroke="currentColor" strokeWidth="1.5" />
                                        </svg>
                                    )}
                                </button>
                            </div>
                            <div className={styles.forgotPassword}>
                                <Link to="/forgot-password">Forgot your password?</Link>
                            </div>
                            <button type="submit" className={styles.submitBtn}>SUBMIT</button>
                        </form>
                        <div className={styles.createAccount}>
                            <Link to="/register">Create an Account</Link>
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
                </div>
            </div>
        </div>
    )
}

export default Login