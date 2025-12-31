import { useEffect, useState } from "react";
import API from "../api";

export default function ExpensesPage() {
  const [expenses, setExpenses] = useState([]);
  const [form, setForm] = useState({});
  const [editing, setEditing] = useState(null);

  const load = async () => {
    const res = await API.get("/expenses/");
    setExpenses(res.data);
  };

  useEffect(() => { load(); }, []);

  const save = async () => {
    if (editing) {
      await API.put(`/expenses/${editing}/`, form);
    } else {
      await API.post(`/expenses/`, form);
    }
    setForm({});
    setEditing(null);
    load();
  };

  const remove = async (id) => {
    if (window.confirm("Delete record?")) {
      await API.delete(`/expenses/${id}/`);
      load();
    }
  };

  return (
    <div className="page-container">
      <h2>Expenses</h2>

      <button onClick={() => window.location.href="http://127.0.0.1:8000/api/expenses/export/"}>
        Export CSV
      </button>

      <div className="form">
        <input type="date"
          value={form.function_date || ""}
          onChange={(e)=>setForm({...form,function_date:e.target.value})}
        />

        <input placeholder="Advance"
          value={form.advance || ""}
          onChange={(e)=>setForm({...form,advance:e.target.value})}
        />

        <button onClick={save}>{editing ? "Update" : "Add"}</button>
      </div>

      <table>
        <thead>
          <tr>
            <th>Date</th><th>Advance</th><th>Balance</th><th>Total</th><th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {expenses.map(e=>(
            <tr key={e.id}>
              <td>{e.function_date}</td>
              <td>{e.advance}</td>
              <td>{e.balance}</td>
              <td>{e.total}</td>
              <td>
                <button onClick={()=>{setForm(e);setEditing(e.id);}}>Edit</button>
                <button onClick={()=>remove(e.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}