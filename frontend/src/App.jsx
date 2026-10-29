import { useEffect, useState } from "react";

export default function App() {
  const [students, setStudents] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/students")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Could not load students from the database");
        }
        return response.json();
      })
      .then((data) => {
        setStudents(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <main className="page">
      <h1>Class roster</h1>
      <p className="lede">Names loaded from the class intake database.</p>
      {loading && <p>Loading…</p>}
      {error && <p className="error">{error}</p>}
      {!loading && !error && (
        <ul className="roster">
          {students.map((student) => (
            <li key={student.netid}>
              <span className="name">{student.name}</span>
              <span className="year">{student.school_year}</span>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
