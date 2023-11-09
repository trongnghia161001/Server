const form = document.querySelector("form"),
  fileInput = document.querySelector(".file-input"),
  progressArea = document.querySelector(".progress-area"),
  uploadedArea = document.querySelector(".uploaded-area");
const wrapper = document.querySelector(".wrapper");
const uploadButton =
  document.getElementById("uploadButton");
// form click event
wrapper.addEventListener("click", () => {
  fileInput.click();
});

fileInput.addEventListener("change", ({ target }) => {
  let file = target.files[0]; // Get the first file if multiple files are selected
  if (file) {
    if (file.name.length >= 12) {
      // If the file name is longer than 12 characters, truncate it and add '...' at the end of the file name
      let splitName = file.name.split(".");
      file.name =
        splitName[0].substring(0, 13) +
        "... ." +
        splitName[1];
    }
    uploadFile(file); // Send file to the upload handler function
  }
});

// file upload function
function uploadFile(file) {
  let xhr = new XMLHttpRequest(); //creating new xhr object (AJAX)
  xhr.open("POST", "upload"); //sending post request to the specified URL

  xhr.upload.addEventListener(
    "progress",
    ({ loaded, total }) => {
      //file uploading progress event
      let fileLoaded = Math.floor((loaded / total) * 100); //getting percentage of loaded file size
      let fileTotal = Math.floor(total / 1000); //gettting total file size in KB from bytes
      let fileSize;
      // if file size is less than 1024 then add only KB else convert this KB into MB
      fileTotal < 1024
        ? (fileSize = fileTotal + " KB")
        : (fileSize =
            (loaded / (1024 * 1024)).toFixed(2) + " MB");

      let progressHTML = `<li class="row">
                        <i class="fas fa-file-alt"></i>
                        <div class="content">
                          <div class="details">
                            <span class="name">${file.name} • Uploading</span>
                            <span class="percent">${fileLoaded}%</span>
                          </div>
                          <div class="progress-bar">
                            <div class="progress" style="width: ${fileLoaded}%"></div>
                          </div>
                        </div>
                      </li>`;

      uploadedArea.classList.add("onprogress");
      progressArea.innerHTML = progressHTML;
      if (loaded === total) {
        progressArea.innerHTML = "";
        let uploadedHTML = `<li class="row">
                          <div class="content upload">
                            <i class="fas fa-file-alt"></i>
                            <div class="details">
                              <span class="name">${file.name} • Uploaded</span>
                              <span class="size">${fileSize}</span>
                            </div>
                          </div>
                          <i class="fas fa-check"></i>
                        </li>`;
        uploadedArea.classList.remove("onprogress");
        uploadedArea.insertAdjacentHTML(
          "afterbegin",
          uploadedHTML
        );
      }
    }
  );

  let data = new FormData();
  data.append("file", file);
  xhr.send(data); //sending form data
}
document
  .querySelector(".center-button")
  .addEventListener("click", () => {
    axios
      .post("/check")
      .then((response) => {
        const userId = response.data; // Lấy ID từ phản hồi của API
        console.log(userId); // In ra ID của người dùng
        const socket = new WebSocket("ws://127.0.0.1:8080");

        socket.onopen = function (event) {
          console.log("Connected to the WebSocket server");
          socket.send(userId); // Gửi ID qua WebSocket khi kết nối được thiết lập
        };
        socket.onmessage = function (event) {
          const receivedData = event.data; // Dữ liệu nhận được từ máy chủ
          if (receivedData.includes("Processed")) {
            // Đây là thông điệp tiến trình
            const progress = parseFloat(
              receivedData
                .split(":")[1]
                .replace("%", "")
                .trim()
            );
            // Hiển thị tiến trình cho người dùng (ví dụ: cập nhật thanh tiến trình)
            updateProgressBar(progress);
          } else {
            // Đây là dữ liệu đã hoàn tất - tạo và hiển thị tệp DOCX
            const blob = new Blob([receivedData], {
              type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            });
            const url = URL.createObjectURL(blob);

            // Hiển thị tệp DOCX trên giao diện
            displayDownloadLink(url);
            hideProgressBar();
          }
        };

        socket.onclose = function (event) {
          console.log("Connection closed");
        };
      })
      .catch((error) => {
        console.error("Có lỗi xảy ra:", error);
      });
  });
function updateProgressBar(progress) {
  const progressBar =
    document.getElementById("progress-bar");
  progressBar.style.width = `${progress}%`;
  progressBar.style.height = "100%";
  progressBar.style.background = "orange";
  progressBar.style.borderRadius = "5px";
  progressBar.style.display = "flex";
  progressBar.style.alignItems = "center";
  progressBar.style.justifyContent = "center";
  progressBar.innerText = `${progress}%`;
}

function hideProgressBar() {
  const progressBar =
    document.getElementById("progress-bar");
  progressBar.style.width = "0px";
  progressBar.style.height = "0px";
  progressBar.style.display = "none";
}

function displayDownloadLink(url) {
  const link = document.createElement("a");
  link.href = url;
  link.download = "generated_file.docx"; // Tên tệp khi người dùng tải xuống
  link.innerHTML = "Download generated_file.docx";
  document.body.appendChild(link);
}
