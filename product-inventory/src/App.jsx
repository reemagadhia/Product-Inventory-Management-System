import './App.css';
import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import 'bootstrap/dist/css/bootstrap.min.css';
import DataTable from 'react-data-table-component';

function App() {
  const [file, setFile] = useState(null);
  const [products, setProducts] = useState([]);
  const fileInputRef = useRef();

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/products");
      setProducts(response.data);
    } catch (error) {
      console.error(error);
      alert("Failed to fetch products");
    }
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return alert("Select a file first!");
    const formData = new FormData();
    formData.append("file", file);

    try {
      await axios.post("http://127.0.0.1:8000/products/upload-excel", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      await fetchProducts();
    } catch (error) {
      console.error(error);
      const detail = error.response?.data?.detail;
      if (typeof detail === "string") {
        alert(detail);
      } else if (detail?.error) {
        alert(detail.error);
      } else {
        alert("Upload failed");
      }
    }
  };

  const handleReset = () => {
    setFile(null);
    setProducts([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const totalProducts = products.length;
  const totalInventoryValue = products.reduce(
    (sum, p) => sum + p["Unit Price"] * p["Quantity"],
    0
  );
  const avgStockAge =
    products.length > 0
      ? Math.round(
          products.reduce((sum, p) => sum + p["Stock Age (Days)"], 0) / products.length
        )
      : 0;

  const columns = [
    { name: 'SKU', selector: row => row['Product SKU'], sortable: true, grow: 3 },
    { name: 'Name', selector: row => row['Product Name'], sortable: true, grow: 6 },
    { name: 'Category', selector: row => row['Category'], sortable: true, grow: 2 },
    { name: 'Purchase Date', selector: row => row['Purchase Date'], sortable: true, grow: 3 },
    { name: 'Unit Price', selector: row => row['Unit Price'], sortable: true, grow: 2 },
    { name: 'Quantity', selector: row => row['Quantity'], sortable: true, grow: 2 },
    { name: 'Stock Age', selector: row => row['Stock Age (Days)'], sortable: true, grow: 2 },
  ];

  const customStyles = {
    headCells: {
      style: {
        fontWeight: 'bold',
        fontSize: '16px',
        border: '1px solid black',
        padding: '20px',
        backgroundColor: '#87CEEB',
      },
    },
    cells: {
      style: {
        border: '1px solid black',
        fontSize: '15px',
        padding: '20px'
      },
    },
    table: {
      style: {
        border: '1px solid black',
        tableLayout: 'auto',
        minWidth: '1300px',
      },
    },
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1 style={{ textAlign: "center", marginTop: "0px", margin: "20px", fontWeight: 'bold', color: "black" }}>Product Inventory</h1>

      <div className="my-3 text-center">
        <input type="file" ref={fileInputRef} onChange={handleFileChange} />
        <button onClick={handleUpload} className="btn btn-secondary mx-2">Upload</button>
        <button onClick={handleReset} className="btn btn-secondary">Reset</button>
      </div>

      {products.length > 0 && (
        <>
          <div className="card mt-3 mb-3" style={{ padding: "20px", maxWidth: "400px", margin: "20px auto", fontSize:"15px"}}>
            <h5 style={{ paddingBottom: "10px", fontWeight: 'bold', color: "black" }}>Inventory Summary</h5>
            <p><strong>Total Products:</strong> {totalProducts}</p>
            <p><strong>Total Inventory Value:</strong> ${totalInventoryValue.toFixed(2)}</p>
            <p><strong>Average Stock Age:</strong> {avgStockAge} days</p>
          </div>

          <DataTable
            columns={columns}
            data={products}
            pagination
            highlightOnHover
            striped
            responsive
            customStyles={customStyles}
            fixedHeader
            dense
          />
        </>
      )}
    </div>
  );
}

export default App;

