const searchInput = document.getElementById("search-input");
const searchBtn = document.getElementById("search-btn");
const resultsContainer = document.getElementById("results-container");
const fileInput = document.getElementById("file-input");
const uploadBtn = document.getElementById("upload-btn");
const uploadStatus = document.getElementById("upload-status");
const documentsList = document.getElementById("documents-list");
const documentsStatus = document.getElementById("documents-status");
const refreshDocumentsBtn = document.getElementById("refresh-documents-btn");

function createResultCard(result, query) {
  const card = document.createElement("div");
  card.textContent = query;
  card.classList.add("result-card");

  const heading = document.createElement("h3");
  heading.textContent = result.title;
  heading.classList.add("result-header");
  card.appendChild(heading);

  const source = document.createElement("p");
  source.textContent = result.filename;
  source.classList.add("result-source");
  card.appendChild(source);

  const score = document.createElement("span");
  score.textContent = (result.score * 100).toFixed(1) + "% match";
  score.classList.add("result-score");
  card.appendChild(score);

  const resultText = document.createElement("p");
  resultText.textContent = result.text;
  resultText.classList.add("result-text");
  card.appendChild(resultText);

  return card;
}

async function loadDocuments() {
  documentsStatus.textContent = "Loading documents...";
  documentsList.replaceChildren();

  try {
    const response = await fetch("http://127.0.0.1:5000/documents");

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Could not load documents.");
    }

    if (data.documents.length === 0) {
      documentsStatus.textContent = "No uploaded documents yet.";
      return;
    }

    documentsStatus.textContent = `${data.documents.length} uploaded document(s)`;

    
data.documents.forEach((doc) => {
    const item = document.createElement("div");
    item.className = "document-item";

    const filename = document.createElement("span");
    filename.className = "document-filename";
    filename.textContent = doc.filename;

    const deleteBtn = document.createElement("button");
    deleteBtn.className = "delete-document-btn";
    deleteBtn.textContent = "Delete";

    deleteBtn.addEventListener("click", async () => {
        const confirmed = window.confirm(
            `Are you sure you want to delete "${doc.filename}"?`
        );

        if (!confirmed) return;

        deleteBtn.disabled = true;
        deleteBtn.textContent = "Deleting...";

        try {
            const response = await fetch(
                `http://127.0.0.1:5000/delete/${encodeURIComponent(doc.filename)}`,
                { method: "DELETE" }
            );

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || "Deletion failed.");
            }

            await loadDocuments();
        } catch (error) {
            window.alert(error.message);
            deleteBtn.disabled = false;
            deleteBtn.textContent = "Delete";
        }
    });

    item.appendChild(filename);
    item.appendChild(deleteBtn);
    documentsList.appendChild(item);
});

  } catch (error) {
    documentsStatus.textContent = error.message;
  }
}

refreshDocumentsBtn.addEventListener("click", loadDocuments);
loadDocuments();

uploadBtn.addEventListener("click", async () => {
  const file = fileInput.files[0];
  if (!file) {
    uploadStatus.textContent = "Please select a file first.";
    return;
  }
  uploadBtn.disabled = true;
  uploadBtn.textContent = "Uploading...";
  uploadStatus.textContent = "Uploading...";
  const formData = new FormData();
  formData.append("file", file);
  try {
    const response = await fetch("http://127.0.0.1:5000/upload", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Upload failed.");
    }

    uploadStatus.textContent = data.message;
  } catch (error) {
    console.error("Upload error:", error);
    uploadStatus.textContent = error.message;
  } finally {
    uploadBtn.disabled = false;
    upload.textContent = "Upload";
  }
});

searchBtn.addEventListener("click", async () => {
  const query = searchInput.value.trim();
  if (query === "") {
    resultsContainer.textContent = "Please enter a question to search";
    return;
  }
  resultsContainer.textContent = "Searching your notes...";
  searchBtn.disabled = true;
  searchBtn.textContent = "Searching...";

  try {
    const response = await fetch("http://127.0.0.1:5000/search", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query: query }),
    });

    if (!response.ok) {
      throw new Error("Search request failed.");
    }

    const data = await response.json();

    resultsContainer.innerHTML = "";

    if (data.results.length === 0) {
      resultsContainer.textContent =
        "No relevant results found. Try a different question.";
      return;
    }

    for (const result of data.results) {
      const card = createResultCard(result);
      resultsContainer.appendChild(card);
    }
  } catch (error) {
    console.error("Search error:", error);
    resultsContainer.textContent = "Something went wrong. Please try again.";
  } finally {
    searchBtn.disabled = false;
    searchBtn.textContent = "Search";
  }
});
