import { useState } from "react";
import styles from "../styles/Home.module.css";

function Home() {
    const [content, setContent] = useState("");
    const [title, setTitle] = useState("");

    return (
        <div className={styles.container}>
            <div className={styles.notesSection}>
                <h2>Notes</h2>
            </div>
            <h2>Create a Note</h2>
            <form>
                <label htmlFor="title">Title:</label>
                <input
                    type="text"
                    id="title"
                    name="title"
                    required
                    onChange={(e) => setTitle(e.target.value)}
                    value={title}
                />
                <label htmlFor="content">Content:</label>
                <textarea
                    id="content"
                    name="content"
                    required
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                ></textarea>
                <input 
                    type="submit" 
                    value="Submit"
                    className={styles.submitBtn}
                />
            </form>
        </div>
    );
}

export default Home;