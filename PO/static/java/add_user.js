document.addEventListener("DOMContentLoaded", () => {
  const saveUserButton = document.querySelector(".red_button");
  const cancelButton = document.querySelector(".gray_button");

  // Save temporary data when clicking "Save user"
  saveUserButton.addEventListener("click", () => {
    const userData = {
      full_name: document.getElementById("full_name").value,
      email_address: document.getElementById("email_address").value,
      username: document.getElementById("username").value,
      password: document.getElementById("password").value,
      user_title: document.getElementById("user_title").value,
      user_level: document.getElementById("user_level").value,
    };

    // Send data to Flask backend using AJAX
    fetch("/add_user", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(userData)
    })
    .then(response => response.json())
    .then(data => {
      if (data.message === "User added successfully!") {
        alert("User added successfully!");

        // Clear the form after saving
        document.getElementById("full_name").value = '';
        document.getElementById("email_address").value = '';
        document.getElementById("username").value = '';
        document.getElementById("password").value = '';
        document.getElementById("user_title").value = '';
        document.getElementById("user_level").value = '';

        // Reload the table with updated user data
        loadUserTable();
      } else {
        alert("Error adding user.");
      }
    })
    .catch(error => console.error('Error:', error));
  });

  // Clear temporary data when clicking "Cancel"
  cancelButton.addEventListener("click", () => {
    localStorage.removeItem("tempUserData");
  });

  // Load users into the table
  function loadUserTable() {
    fetch("/get_users")
      .then(response => response.json())
      .then(users => {
        const tableBody = document.querySelector("#manage_users_table tbody");
        tableBody.innerHTML = ""; // Clear existing table rows

        users.forEach(user => {
          const row = document.createElement("tr");

          row.innerHTML = `
            <td>${user.full_name}</td>
            <td>${user.email_address}</td>
            <td>${user.username}</td>
            <td>${user.user_title}</td>
            <td>${user.user_level}</td>
            <td class="action_buttons">
              <button class="btn btn-warning edit_button" data-bs-toggle="modal" data-bs-target="#edit_user_modal">
                <i class="fa-solid fa-pen-to-square"></i> Edit
              </button>
            </td>
          `;
          tableBody.appendChild(row);
        });
      })
      .catch(error => console.error('Error loading users:', error));
  }

  // Load initial users when the page is ready
  loadUserTable();
});
