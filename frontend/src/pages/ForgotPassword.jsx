import styles from "../styles/Form.module.css"
import { useState } from "react"
import api from "../api"
import { useNavigate, Link } from "react-router-dom"

function ForgotPassword() {
    const [email, setEmail] = useState("")
    const navigate = useNavigate()

    const handleSubmit = async (e) => {
        e.preventDefault()
        try {
            await api.post("/users/reset-password/", { email })
            alert("Password reset instructions have been sent to your email")
            navigate("/login")
        } catch (error) {
            alert(error)
        }
    }

    return (
        <div className={styles.body}>
            <div className={styles.form}>
                <div className={styles.container}>
                    <div className={styles.imageSection}>
                        <img src="https://static.tildacdn.com/stor3238-6634-4332-a461-353137663739/48396303.jpg" alt="African woman in headwrap" />
                    </div>
                    <div className={styles.loginSection}>
                        <div className={styles.loginHeader}>
                            <h1>RESTORE PASSWORD</h1>
                        </div>
                        <form id="reset-password-form" onSubmit={handleSubmit}>
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
                            <button type="submit" className={styles.submitBtn}>SEND RESET INSTRUCTIONS</button>
                        </form>
                        <div className={styles.createAccount}>
                            <Link to="/login">Back to Login</Link>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default ForgotPassword