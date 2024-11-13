document.addEventListener("DOMContentLoaded", () => {
  const addUserButton = document.getElementById("addUserButton");
  const saveUserButton = document.getElementById("saveUserButton");
  const saveEditUserButton = document.getElementById("saveEditUserButton");
  let currentUserId; // Track the current user being edited

  // Initialize DataTable
  const dataTable = new DataTable("#manage_users_table", {
    layout: {
      top9Start: {
        pageLength: {
          menu: [10, 25, 50, 100],
        },
      },
      top9End: {
        search: {
          placeholder: "Search...",
        },
      },
      bottomEnd: {
        paging: {
          className: "paging_custom",
          buttons: 4,
        },
      },
      topStart: {
        buttons: [
          { extend: "copy", className: "custom_button", text: "Copy" },
          { extend: "csv", className: "custom_button", text: "CSV" },
          { extend: "excel", className: "custom_button", text: "Excel" },
          { extend: "pdf", className: "custom_button", text: "PDF" },
          { extend: "print", className: "custom_button", text: "Print" },
        ],
      },
      topEnd: addUserButton,
    },
    language: {
      lengthMenu: "Show _MENU_ entries per page",
      search: "Filter:",
    },
  });

  // Function to add user to the table dynamically
  function addUserToTable(user) {
    const tableBody = document.querySelector("#manage_users_table tbody");
    const row = document.createElement("tr");

    row.innerHTML = `
      <td>${user.full_name}</td>
      <td>${user.email_address}</td>
      <td>${user.username}</td>
      <td>${user.user_title}</td>
      <td>${user.user_level}</td>
      <td class="action_buttons">
 <button type="button" class="btn btn-primary" onclick="loadUserDataIntoEditModal({{ user.id }})">
      Edit
    </button>
</td>

      </td>
    `;
    tableBody.appendChild(row);
    dataTable.update();
  }

  // Save new user data and update the table
  saveUserButton.addEventListener("click", () => {
    const userData = {
      full_name: document.getElementById("full_name").value,
      email_address: document.getElementById("email_address").value,
      username: document.getElementById("username").value,
      password: document.getElementById("password").value,
      user_title: document.getElementById("user_title").value,
      user_level: document.getElementById("user_level").value,
    };

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
        addUserToTable(data.user);
        document.getElementById("addUserForm").reset();
      } else {
        alert("Error adding user.");
      }
    })
    .catch(error => console.error('Error:', error));
  });

  // Load users initially
  function loadUserTable() {
    fetch("/get_users")
      .then(response => response.json())
      .then(users => {
        const tableBody = document.querySelector("#manage_users_table tbody");
        tableBody.innerHTML = "";
        users.forEach(user => addUserToTable(user));
        dataTable.update();
      })
      .catch(error => console.error('Error loading users:', error));
  }

  // Load user data into edit modal
  document.addEventListener("click", event => {
    if (event.target.closest(".edit_button")) {
      currentUserId = event.target.closest(".edit_button").dataset.userId;
      loadUserDataIntoEditModal(currentUserId);
    }
  });

  function loadUserDataIntoEditModal(userId) {
  fetch(`/get_user/${userId}`)
    .then(response => {
      if (!response.ok) {
        throw new Error("User not found");
      }
      return response.json();
    })
    .then(user => {
      document.getElementById("edit_full_name").value = user.full_name || "";
      document.getElementById("edit_email_address").value = user.email_address || "";
      document.getElementById("edit_username").value = user.username || "";
      document.getElementById("edit_password").value = user.password || "";
      document.getElementById("edit_user_title").value = user.user_title || "";
      document.getElementById("edit_user_level").value = user.user_level || "";
      $('#editModal').modal('show');  // Show the modal after data loads
    })
    .catch(error => console.error("Error loading user data:", error));
}



  // Save changes for the edited user
  saveEditUserButton.addEventListener("click", () => {
    const updatedUserData = {
      full_name: document.getElementById("edit_full_name").value,
      email_address: document.getElementById("edit_email_address").value,
      username: document.getElementById("edit_username").value,
      password: document.getElementById("edit_password").value,
      user_title: document.getElementById("edit_user_title").value,
      user_level: document.getElementById("edit_user_level").value,
    };

    fetch(`/update_user/${currentUserId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(updatedUserData)
    })
    .then(response => response.json())
    .then(data => {
      if (data.message === "User updated successfully!") {
        loadUserTable();  // Refresh the table to show updated info
      } else {
        alert("Error updating user.");
      }
    })
    .catch(error => console.error('Error updating user:', error));
  });

  // Load the users into the table on page load
  loadUserTable();
});
