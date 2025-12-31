import { useEffect, useState } from "react";
import API from "../api";

export default function ExpensesPage() {
  const [expenses, setExpenses] = useState([]);
  const [form, setForm] = useState({});
  const [editing, setEditing] = useState(null);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);

  const load = async () => {
    try {
      const res = await API.get("/expenses/");
      setExpenses(res.data);
    } catch (err) {
      console.error("Error loading expenses:", err);
      setError(err.response?.data || "Failed to load expenses");
    }
  };

  useEffect(() => { load(); }, []);

  const save = async () => {
    try {
      setError("");
      if (editing) {
        await API.put(`/expenses/${editing}/`, form);
      } else {
        await API.post(`/expenses/`, form);
      }
      setForm({});
      setEditing(null);
      setShowForm(false);
      load();
      alert(editing ? "Record updated!" : "Record added!");
    } catch (err) {
      console.error("Error saving expense:", err);
      console.error("Error details:", err.response?.data);
      setError(err.response?.data || "Failed to save expense");
    }
  };

  const remove = async (id) => {
    if (window.confirm("Delete record?")) {
      try {
        await API.delete(`/expenses/${id}/`);
        load();
        alert("Record deleted!");
      } catch (err) {
        console.error("Error deleting expense:", err);
        setError(err.response?.data || "Failed to delete expense");
      }
    }
  };

  const handleEdit = (expense) => {
    setForm(expense);
    setEditing(expense.id);
    setShowForm(true);
    setError("");
  };

  const handleCancel = () => {
    setForm({});
    setEditing(null);
    setShowForm(false);
    setError("");
  };

  const renderErrors = () => {
    if (!error) return null;

    if (typeof error === "string") {
      return <div className="error-box">{error}</div>;
    }

    return (
      <div className="error-box">
        {Object.entries(error).map(([field, messages]) => (
          <p key={field}>
            <strong>{field}:</strong>{" "}
            {Array.isArray(messages) ? messages.join(", ") : messages}
          </p>
        ))}
      </div>
    );
  };

  return (
    <div className="page-container">
      <h2>Expenses</h2>

      {renderErrors()}

      <div className="action-buttons">
        <button 
          className="btn-add-new"
          onClick={() => {
            setShowForm(true);
            setForm({});
            setEditing(null);
            setError("");
          }}
        >
          + Add New Expense
        </button>
        
        <button 
          className="btn-export"
          onClick={() => window.location.href="http://127.0.0.1:8000/api/expenses/export/"}
        >
          Export CSV
        </button>
      </div>

      <table>
        <thead>
          <tr>
            <th>Function Date</th>
            <th>Advance</th>
            <th>Balance</th>
            <th>Damage Recovery</th>
            <th>Gens</th>
            <th>Ladies</th>
            <th>Flag</th>
            <th>Waste Room Cleanin</th>
            <th>Electrician</th>
            <th>Radio</th>
            <th>Light</th>
            <th>Total</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {expenses.map(e=>(
            <tr key={e.id}>
              <td>{e.function_date}</td>
              <td>{e.advance || 0}</td>
              <td>{e.balance || 0}</td>
              <td>{e.damage_recovery || 0}</td>
              <td>{e.gens || 0}</td>
              <td>{e.ladies || 0}</td>
              <td>{e.flag || 0}</td>
              <td>{e.waste_room_cleanin || 0}</td>
              <td>{e.electrician || 0}</td>
              <td>{e.radio || 0}</td>
              <td>{e.light || 0}</td>
              <td>{e.total || 0}</td>
              <td>
                <button onClick={()=>handleEdit(e)}>Edit</button>
                <button onClick={()=>remove(e.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {showForm && (
        <div className="modal-overlay" onClick={handleCancel}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editing ? "Edit Expense" : "Add New Expense"}</h3>
              <button className="modal-close" onClick={handleCancel}>×</button>
            </div>
            
            <div className="form">
              <input 
                type="date"
                placeholder="Function Date"
                value={form.function_date || ""}
                onChange={(e)=>setForm({...form, function_date: e.target.value})}
              />

              <input 
                placeholder="Advance"
                type="number"
                value={form.advance || ""}
                onChange={(e)=>setForm({...form, advance: e.target.value})}
              />

              <input 
                placeholder="Balance"
                type="number"
                value={form.balance || ""}
                onChange={(e)=>setForm({...form, balance: e.target.value})}
              />

              <input 
                placeholder="Damage Recovery"
                type="number"
                value={form.damage_recovery || ""}
                onChange={(e)=>setForm({...form, damage_recovery: e.target.value})}
              />

              <input 
                placeholder="Gens"
                type="number"
                value={form.gens || ""}
                onChange={(e)=>setForm({...form, gens: e.target.value})}
              />

              <input 
                placeholder="Ladies"
                type="number"
                value={form.ladies || ""}
                onChange={(e)=>setForm({...form, ladies: e.target.value})}
              />

              <input 
                placeholder="Flag"
                type="number"
                value={form.flag || ""}
                onChange={(e)=>setForm({...form, flag: e.target.value})}
              />

              <input 
                placeholder="Waste Room Cleanin"
                type="number"
                value={form.waste_room_cleanin || ""}
                onChange={(e)=>setForm({...form, waste_room_cleanin: e.target.value})}
              />

              <input 
                placeholder="Electrician"
                type="number"
                value={form.electrician || ""}
                onChange={(e)=>setForm({...form, electrician: e.target.value})}
              />

              <input 
                placeholder="Radio"
                type="number"
                value={form.radio || ""}
                onChange={(e)=>setForm({...form, radio: e.target.value})}
              />

              <input 
                placeholder="Light"
                type="number"
                value={form.light || ""}
                onChange={(e)=>setForm({...form, light: e.target.value})}
              />
            </div>

            <div className="modal-footer">
              <button className="btn-save" onClick={save}>
                {editing ? "Update" : "Save"}
              </button>
              <button className="btn-cancel" onClick={handleCancel}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}