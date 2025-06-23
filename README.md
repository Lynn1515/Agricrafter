# Agricrafter

🚧 **The project is under code cleanup and organization. Stay tuned!**

**Agricrafter** leverages video diffusion models to realistically simulate crop growth, generating full-growth-cycle videos from a single image.

The repository is currently being prepared for public release. Core components, models, and detailed documentation will be available soon.

## 📌 Project Overview
- Crop growth Dataset
- Crop growth video generation from images
- Support for long-range generation
- Support for control parameters

## 🧬 1. Crop Growth Dataset Construction

We build a crop growth video dataset capturing full life cycles.

<div align="center">
  <img src="assets/dataset-1.png" width="600" alt="Dataset Sample Image"/>
  <p><em>Figure: Example frame from our constructed crop growth dataset.</em></p>
</div>

---

## 🆚 2. Comparison with Baseline Methods

We compare Agricrafter with baseline methods on realistic crop growth generation. The first column is the output from baseline methods, and the second column is from our Agricrafter.

<h4 align="center">🔁 Column 1: Baseline Outputs   |   Column 2: Agricrafter (Ours)</h4>

<table>
  <tr>
    <th style="text-align:center">Baseline</th>
    <th style="text-align:center">Agricrafter (Ours)</th>
  </tr>
  <tr>
    <td align="center">
      <video src="https://github.com/user-attachments/assets/c7a32569-e1cc-4727-afc9-0a721f5ee2b8" controls width="80">
      </video>
    </td>
    <td align="center">
      <video src="https://github.com/user-attachments/assets/5544987a-f209-42e3-8554-8c46c5063eb2" controls width="80">
      </video>
    </td>
  </tr>
  <tr>
    <td align="center">
      <video src="https://github.com/user-attachments/assets/a66cd49b-26e8-4312-9710-2bb438e4336f" controls width="80">
      </video>
    </td>
    <td align="center">
      <video src="https://github.com/user-attachments/assets/761ee9f0-39a4-4ddc-b242-1a8a1287fccd" controls width="80">
      </video>
    </td>
  </tr>
  <tr>
    <td align="center">
      <video src="https://github.com/user-attachments/assets/9bf91685-a9c3-47f8-8567-e75dfb1ffa23" controls width="80">
      </video>
    </td>
    <td align="center">
      <video src="https://github.com/user-attachments/assets/69ed3bb3-ed86-40a4-baea-12d91c509df7" controls width="80">
      </video>
    </td>
  </tr>
    <tr>
    <td align="center">
      <video src="https://github.com/user-attachments/assets/80c23bed-9f76-406d-bc55-183cdb3460da" controls width="80">
      </video>
    </td>
    <td align="center">
      <video src="https://github.com/user-attachments/assets/7128cad4-a188-4f11-99d7-7df508d75ed2" controls width="80">
      </video>
    </td>
  </tr>
</table>

---

## 🔁 3. Long-Term Generation via Frame Interpolation

Agricrafter supports **long-range video synthesis** by interpolating intermediate states from short growth clips.

### 🧠 Model Principle

<div align="center">
  <img src="assets/interpolation-1.png" width="500" alt="Interpolation Principle"/>
  <p><em>Figure: Interpolation-based long video generation.</em></p>
</div>

### 🎞️ Video Comparison: Short Video vs. Interpolated Long Video

<table>
  <tr>
    <th style="text-align:center">Short Video Input</th>
    <th style="text-align:center">Long Video Output (Interpolated)</th>
  </tr>
  <tr>
    <td align="center">
      <video src="https://github.com/user-attachments/assets/b683000e-9412-4bfe-9d38-707c2ef6a177" controls width="100">
      </video>
    </td>
    <td align="center">
      <video src="https://github.com/user-attachments/assets/06390bd7-1866-4dd3-ae4f-a007c033ebf7" controls width="100">
      </video>
    </td>
  </tr>
  <tr>
    <td align="center">
      <video src="https://github.com/user-attachments/assets/76d4ea3c-d608-44f1-95de-0217c9d6caf5" controls width="100">
      </video>
    </td>
    <td align="center">
      <video src="https://github.com/user-attachments/assets/dd81f91b-88ca-405c-b333-d2e635a28360" controls width="100">
      </video>
    </td>
  </tr>
  <tr>
    <td align="center">
      <video src="https://github.com/user-attachments/assets/47ddc2e2-a68f-4f0d-9864-9d8a00bdc3b7" controls width="100">
      </video>
    </td>
    <td align="center">
      <video src="https://github.com/user-attachments/assets/1606ef13-e4e8-42d0-83f8-8c21677b82c0" controls width="100">
      </video>
    </td>
  </tr>
</table>

---


## 📂 Crop Growth Dataset (Coming Soon)

## 🔧 Installation and Usage (Coming Soon)

## 📄 License
This project will be released under the Apache2.0 License.

---

Feel free to watch or star this repository. We will continuously update and improve the codebase and documentation!
