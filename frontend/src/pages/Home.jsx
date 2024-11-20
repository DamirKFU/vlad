import { useState } from "react";
import api from "../api";
import "../styles/Home.css"

function Home() {
    const [content, setContent] = useState("");
    const [title, setTitle] = useState("");

    return (
        <div>
            <div>
                <h2>Notes</h2>
            </div>
            <h2>Create a Note</h2>
            <form>
                <label htmlFor="title">Title:</label>
                <br />
                <input
                    type="text"
                    id="title"
                    name="title"
                    required
                    onChange={(e) => setTitle(e.target.value)}
                    value={title}
                />
                <label htmlFor="content">Content:</label>
                <br />
                <textarea
                    id="content"
                    name="content"
                    required
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                ></textarea>
                <br />
                <input type="submit" value="Submit"></input>
            </form>
        </div>
    );
}

export default Home;