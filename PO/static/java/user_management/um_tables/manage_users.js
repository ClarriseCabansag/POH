document.addEventListener("DOMContentLoaded", () => {
  const addUserButton = document.getElementById("addUserButton");
  const saveUserButton = document.getElementById("saveUserButton");

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
          {
            extend: "copy",
            className: "custom_button",
            text: "Copy",
          },
          {
            extend: "csv",
            className: "custom_button",
            text: "CSV",
          },
          {
            extend: "excel",
            className: "custom_button",
            text: "Excel",
          },
          {
            extend: "pdf",
            className: "custom_button",
            text: "PDF",
          },
          {
            extend: "print",
            className: "custom_button",
            text: "Print",
          },
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
        <button class="btn btn-warning edit_button" data-bs-toggle="modal" data-bs-target="#edit_user_modal">
          <i class="fa-solid fa-pen-to-square"></i> Edit
        </button>
      </td>
    `;
    tableBody.appendChild(row);
    dataTable.update();  // Refresh DataTable to include the new row
  }

  // Load users initially
  loadUserTable();

  function loadUserTable() {
    fetch("/get_users")
      .then(response => response.json())
      .then(users => {
        const tableBody = document.querySelector("#manage_users_table tbody");
        tableBody.innerHTML = ""; // Clear existing rows

        users.forEach(user => {
          addUserToTable(user);
        });

        dataTable.update();  // Update DataTable after loading all users
      })
      .catch(error => console.error('Error loading users:', error));
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
        // Show success message without user needing to click "OK"
        const successAlert = document.createElement("div");
        successAlert.classList.add("alert", "alert-success");
        successAlert.textContent = "User added successfully!";
        document.body.appendChild(successAlert);

        // Hide the success message after 3 seconds
        setTimeout(() => {
          successAlert.remove();
        }, 3000);

        // Add user to the table without reloading
        addUserToTable(data.user);

        // Clear the form fields
        document.getElementById("addUserForm").reset();

        // Find the modal element and hide it
        const addUserModalElement = document.getElementById("add_user_modal");
        const addUserModal = new bootstrap.Modal(addUserModalElement);
        addUserModal.hide();  // Programmatically close the modal
      } else {
        alert("Error adding user.");
      }
    })
    .catch(error => console.error('Error:', error));
  });

  // Automatically show the modal when the "Add User" button is clicked
  addUserButton.addEventListener("click", () => {
    // Reset the form when the "Add User" button is clicked
    document.getElementById("addUserForm").reset();

    // Show the modal form
    const addUserModalElement = document.getElementById("add_user_modal");
    const addUserModal = new bootstrap.Modal(addUserModalElement);
    addUserModal.show();
  });
});
