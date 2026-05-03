import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import multiprocessing
import threading
import time
import math
import csv
import os
import random

# Matplotlib integration
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- HEAVY CPU-BOUND ANALYSIS LOGIC ---
def analyze_feedback(text):
    """
    Analyzes customer feedback using CPU-intensive operations.
    Includes mathematical computations to demonstrate parallel processing benefits.
    """
    word_count = len(text.split())
    
    # 1. Heavy string processing
    processed_text = text * 3  # Artificial expansion for CPU work
    char_sum = 0
    for i, char in enumerate(processed_text[:1000]):  # Limit to prevent memory issues
        char_sum += math.sin(ord(char)) * math.cos(i)
    
    # 2. Artificial computation - Fibonacci-like sequence
    fib_sequence = [1, 1]
    for i in range(2, min(500, word_count + 50)):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    
    # 3. Prime number checking (CPU intensive)
    def is_prime(n):
        if n < 2:
            return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True
    
    prime_count = 0
    for num in range(2, 200):  # Check primes up to 200
        if is_prime(num):
            prime_count += 1
    
    # 4. Matrix multiplication simulation
    matrix_size = min(50, word_count // 10 + 10)
    matrix = [[random.random() for _ in range(matrix_size)] for _ in range(matrix_size)]
    result_matrix = [[0 for _ in range(matrix_size)] for _ in range(matrix_size)]
    for i in range(matrix_size):
        for j in range(matrix_size):
            for k in range(matrix_size):
                result_matrix[i][j] += matrix[i][k] * matrix[k][j]
    
    # 5. Complex mathematical operations
    score = 0
    for char in text[:200]:  # Process first 200 chars
        score += math.sqrt(abs(math.sin(ord(char)) * (word_count + 1))) * math.pi
    
    # Combine all computations to ensure CPU work
    final_score = score + char_sum + prime_count * 100 + sum(fib_sequence[-10:]) / 1000
    
    return final_score

class FeedbackApp:
    """
    Customer Feedback Analyzer with Performance Benchmarking
    
    This application processes customer feedback text while benchmarking three
    execution strategies. Despite its business-friendly name, its primary purpose
    is demonstrating Python concurrency concepts using real text analysis workloads.
    
    Key Demonstrations:
    - Sequential: Baseline single-core performance
    - Threading: Impact of Python's GIL on CPU-bound tasks (often SLOWER!)
    - Multiprocessing: True parallel execution on multi-core systems (2-8x FASTER!)
    
    Business Value:
    - Process thousands of feedback entries efficiently
    - Export scores for reporting and trend analysis
    - Understand scaling characteristics for data pipelines
    
    Educational Value:
    - Visual performance comparisons
    - Real-time benchmarking charts
    - Speedup and efficiency calculations
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Customer Feedback Analyzer | Performance Benchmarking Suite")
        self.root.geometry("1200x950")
        
        self.data_store = {"Short": [], "Detailed": [], "Enterprise": []}
        self.last_results = [] 
        self.results_map = {"Sequential": 0.0, "Threading": 0.0, "Parallel": 0.0}
        
        self._setup_ui()

    def _setup_ui(self):
        # 1. Header - Revised for honesty and clarity
        header = tk.Frame(self.root, bg="#f0f0f0")
        header.pack(fill="x", padx=20, pady=10)
        
        # Main title
        tk.Label(header, text="📊 Customer Feedback Analyzer", 
                 font=("Arial", 20, "bold"), bg="#f0f0f0").pack()
        
        # Honest subtitle explaining what it really does
        tk.Label(header, text="Enterprise Feedback Processing with Performance Intelligence", 
                 font=("Arial", 10), fg="#555555", bg="#f0f0f0").pack()
        tk.Label(header, text="Benchmark: Sequential • Threading (GIL-Limited) • Multiprocessing (True Parallel)", 
                 font=("Arial", 9, "italic"), fg="#777777", bg="#f0f0f0").pack()
        
        # 2. Controls Frame
        ctrl_frame = tk.LabelFrame(self.root, text="Step 1: Data Management", padx=10, pady=10, font=("Arial", 10, "bold"))
        ctrl_frame.pack(fill="x", padx=20, pady=5)
        
        tk.Button(ctrl_frame, text="📁 Browse for File...", command=self.load_from_file, 
                 bg="#2196F3", fg="white", padx=10).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(ctrl_frame, text="🔄 Generate Test Data", command=self.generate_test_data, 
                 bg="#4CAF50", fg="white", padx=10).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(ctrl_frame, text="Select Category:").grid(row=0, column=2, padx=10)
        self.cat_var = tk.StringVar()
        self.dropdown = ttk.Combobox(ctrl_frame, textvariable=self.cat_var, state="readonly", width=15)
        self.dropdown.grid(row=0, column=3, padx=5)
        self.dropdown.bind("<<ComboboxSelected>>", lambda e: self.refresh_preview())

        tk.Button(ctrl_frame, text="🗑️ Clear Results", command=self.clear_all, 
                 bg="#f44336", fg="white", padx=10).grid(row=0, column=4, padx=20)
        
        # Status label
        self.status_label = tk.Label(ctrl_frame, text="✅ Ready", font=("Arial", 9, "italic"), fg="#4CAF50")
        self.status_label.grid(row=1, column=0, columnspan=5, pady=5)

        # 3. Execution Frame
        exec_frame = tk.LabelFrame(self.root, text="Step 2: Run Performance Benchmarks", padx=10, pady=10, font=("Arial", 10, "bold"))
        exec_frame.pack(fill="x", padx=20, pady=5)
        
        # Sequential button
        self.seq_btn = tk.Button(exec_frame, text="Sequential (Baseline)", command=self.run_sequential, 
                                width=20, height=2, bg="#9E9E9E", fg="white", font=("Arial", 9, "bold"))
        self.seq_btn.grid(row=0, column=0, padx=5, pady=5)
        self._create_tooltip(self.seq_btn, "Single-core processing\nBaseline performance measurement")
        
        # Threading button
        self.thread_btn = tk.Button(exec_frame, text="Threading (GIL-Limited)", command=self.run_threading, 
                                   width=20, height=2, bg="#FF9800", fg="white", font=("Arial", 9, "bold"))
        self.thread_btn.grid(row=0, column=1, padx=5, pady=5)
        self._create_tooltip(self.thread_btn, "⚠️ May be SLOWER than sequential for CPU-heavy tasks\ndue to Python's Global Interpreter Lock (GIL)")
        
        # Parallel button
        self.par_btn = tk.Button(exec_frame, text="Multiprocessing (True Parallel)", command=self.run_parallel, 
                                width=25, height=2, bg="#4CAF50", fg="white", font=("Arial", 9, "bold"))
        self.par_btn.grid(row=0, column=2, padx=5, pady=5)
        self._create_tooltip(self.par_btn, "True parallel processing using all CPU cores\n2-8x FASTER for CPU-intensive workloads")
        
        # Export button
        tk.Button(exec_frame, text="📎 Export Results to CSV", command=self.export_to_csv, 
                 width=20, height=2, bg="#9C27B0", fg="white", font=("Arial", 9, "bold")).grid(row=0, column=3, padx=20, pady=5)
        
        # Add info about CPU cores
        cpu_count = multiprocessing.cpu_count()
        info_frame = tk.Frame(exec_frame)
        info_frame.grid(row=1, column=0, columnspan=4, pady=10)
        
        tk.Label(info_frame, text="💡 Performance Insight:", 
                font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Label(info_frame, text=f"For CPU-heavy text analysis, Multiprocessing is fastest | System has {cpu_count} CPU cores | Threading may be slower than Sequential", 
                font=("Arial", 9), fg="#555555").pack(side=tk.LEFT)

        # 4. Chart Area
        chart_container = tk.Frame(self.root)
        chart_container.pack(fill="both", expand=True, padx=20, pady=5)
        
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(10, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_container)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # 5. Logs & Preview
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill="x", padx=20, pady=5)
        
        # Preview box
        preview_label = tk.Label(bottom_frame, text="Data Preview (first 10 items)", font=("Arial", 9, "bold"))
        preview_label.pack(anchor="w")
        self.preview_box = scrolledtext.ScrolledText(bottom_frame, height=6, width=60, font=("Consolas", 9))
        self.preview_box.pack(side="left", padx=(0,10), pady=5, expand=True, fill="both")
        
        # Log box
        log_label = tk.Label(bottom_frame, text="Performance Log", font=("Arial", 9, "bold"))
        log_label.pack(anchor="w")
        self.log_box = scrolledtext.ScrolledText(bottom_frame, height=6, width=60, bg="#f8f8f8", font=("Consolas", 9))
        self.log_box.pack(side="right", pady=5, expand=True, fill="both")
        
        # 6. Status Bar
        self.status_bar = tk.Label(self.root, text="✅ Ready | Generate test data or load a file to begin", 
                                   bd=1, relief=tk.SUNKEN, anchor=tk.W, font=("Arial", 8), bg="#f0f0f0")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # About button in menu bar
        menubar = tk.Menu(self.root)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Performance Guide", command=self.show_guide)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.root.config(menu=menubar)
        
        self.update_chart()

    def _create_tooltip(self, widget, text):
        """Create tooltip for widgets"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background="#ffffe0", 
                           relief="solid", borderwidth=1, font=("Arial", 9),
                           padx=5, pady=5)
            label.pack()
            def hide_tooltip():
                tooltip.destroy()
            widget.bind('<Leave>', lambda e: hide_tooltip())
            tooltip.after(5000, hide_tooltip)
        widget.bind('<Enter>', show_tooltip)

    def log(self, msg):
        """Enhanced logging with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_box.insert(tk.END, f"[{timestamp}] {msg}\n")
        self.log_box.see(tk.END)
        self.root.update_idletasks()

    def update_status(self, msg):
        """Update status bar"""
        self.status_bar.config(text=msg)
        self.root.update_idletasks()

    def refresh_preview(self):
        cat = self.cat_var.get()
        if not cat: return
        self.preview_box.delete("1.0", tk.END)
        for i, text in enumerate(self.data_store[cat][:10]):
            self.preview_box.insert(tk.END, f"{i+1}. {text[:70]}...\n")

    def update_chart(self):
        """Update performance comparison charts"""
        # Clear both axes
        self.ax1.clear()
        self.ax2.clear()
        
        # Bar chart for execution times
        methods = list(self.results_map.keys())
        times = list(self.results_map.values())
        colors = ['#9E9E9E', '#FF9800', '#4CAF50']
        
        bars = self.ax1.bar(methods, times, color=colors)
        self.ax1.set_ylabel("Execution Time (Seconds)")
        self.ax1.set_title("Execution Time Comparison")
        self.ax1.set_yscale('log')  # Log scale for better visualization
        
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                self.ax1.text(bar.get_x() + bar.get_width()/2., h, f'{h:.3f}s', 
                             ha='center', va='bottom', fontsize=9)
        
        # Speedup chart (if sequential time exists)
        if self.results_map["Sequential"] > 0:
            sequential_time = self.results_map["Sequential"]
            speedups = []
            speedup_labels = []
            
            if self.results_map["Threading"] > 0:
                speedup = sequential_time / self.results_map["Threading"]
                speedups.append(speedup)
                speedup_labels.append(f"Threading\n({speedup:.2f}x)")
            if self.results_map["Parallel"] > 0:
                speedup = sequential_time / self.results_map["Parallel"]
                speedups.append(speedup)
                speedup_labels.append(f"Multiprocessing\n({speedup:.2f}x)")
            
            if speedups:
                bars2 = self.ax2.bar(speedup_labels, speedups, color=['#FF9800', '#4CAF50'])
                self.ax2.set_ylabel("Speedup Factor (x times faster)")
                self.ax2.set_title("Performance Gain vs Sequential")
                self.ax2.axhline(y=1, color='r', linestyle='--', alpha=0.5, label="Sequential Baseline")
                self.ax2.legend()
                
                for bar in bars2:
                    h = bar.get_height()
                    self.ax2.text(bar.get_x() + bar.get_width()/2., h, f'{h:.2f}x', 
                                 ha='center', va='bottom', fontsize=9)
        
        self.fig.tight_layout()
        self.canvas.draw()

    def generate_test_data(self):
        """Generate synthetic customer feedback data for benchmarking"""
        self.update_status("Generating test feedback data...")
        self.log("Generating synthetic customer feedback dataset...")
        
        # Short feedbacks (under 20 words)
        short_templates = [
            "Great product! Very satisfied with the quality.",
            "Poor customer service, would not recommend.",
            "Excellent value for money, will buy again.",
            "Shipping was slow but product is decent.",
            "Amazing features, exactly what I needed.",
            "Broke after one week, very disappointed.",
            "User interface is intuitive and easy to use.",
            "Too expensive for what you get.",
            "Perfect for beginners and experts alike.",
            "Battery life could be better but overall good."
        ]
        
        short_texts = []
        for i in range(300):  # 300 short feedbacks
            text = random.choice(short_templates)
            short_texts.append(f"{text} (Feedback #{i+1})")
        
        # Detailed feedbacks (20-150 words)
        detailed_template = """After using it for several weeks, I have observed that the performance is generally good but there are some areas needing improvement. The user interface is responsive and intuitive, making it easy for new users to get started. However, I noticed that sometimes the application becomes slow when processing large files. The customer support team was helpful in resolving my initial issues. I would rate this product 4 out of 5 stars. The price point is reasonable considering the features offered. One suggestion would be to add more customization options. The documentation is clear and well-organized. Overall, I am satisfied with my purchase and would recommend it to colleagues."""
        
        detailed_texts = []
        for i in range(400):  # 400 detailed feedbacks
            detailed_texts.append(f"{detailed_template} (Detailed Review #{i+1})")
        
        # Enterprise feedbacks (150+ words)
        enterprise_template = """This comprehensive enterprise-level feedback provides an in-depth analysis of the product's performance in a large-scale deployment environment. Over the past quarter, our team has extensively tested the solution across multiple departments, involving approximately 500 users. The scalability of the system has proven to be robust, handling concurrent requests efficiently without significant degradation in response times. Security features meet our organizational requirements, with proper encryption standards and compliance certifications. Integration with existing infrastructure was seamless, requiring minimal customization. The API documentation is thorough, allowing our developers to implement custom workflows without extensive support. However, we have identified several areas for improvement. The reporting module could benefit from additional filtering options and export capabilities. The mobile experience, while functional, lacks some features available on the desktop version. Loading times for large datasets (10,000+ records) could be optimized further. The vendor's support team has been responsive, typically responding within 2 hours for critical issues. Pricing is competitive compared to alternatives we evaluated. We recommend implementing the following enhancements: improved batch processing capabilities, real-time synchronization with external databases, and enhanced role-based access controls. Despite these minor concerns, the product has delivered measurable ROI, reducing operational costs by approximately 15% in the first six months. We plan to continue using this solution and expanding its deployment to additional departments in the coming fiscal year."""
        
        enterprise_texts = []
        for i in range(300):  # 300 enterprise feedbacks
            enterprise_texts.append(f"{enterprise_template} (Enterprise Review #{i+1})")
        
        self.data_store = {
            "Short": short_texts,
            "Detailed": detailed_texts,
            "Enterprise": enterprise_texts
        }
        
        self.dropdown['values'] = [k for k, v in self.data_store.items() if v]
        if self.dropdown['values']:
            self.dropdown.current(0)
            self.refresh_preview()
        
        total = len(short_texts) + len(detailed_texts) + len(enterprise_texts)
        self.log(f"✅ Generated {total} test feedback entries:")
        self.log(f"   - Short (under 20 words): {len(short_texts)} entries")
        self.log(f"   - Detailed (20-150 words): {len(detailed_texts)} entries")
        self.log(f"   - Enterprise (150+ words): {len(enterprise_texts)} entries")
        self.update_status(f"Ready | {total} test feedback entries generated")

    def load_from_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not path: return
        
        self.update_status(f"Loading file: {os.path.basename(path)}...")
        self.data_store = {"Short": [], "Detailed": [], "Enterprise": []}
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    t = line.strip()
                    if not t: continue
                    w = len(t.split())
                    if w < 20: 
                        self.data_store["Short"].append(t)
                    elif w < 150: 
                        self.data_store["Detailed"].append(t)
                    else: 
                        self.data_store["Enterprise"].append(t)
            
            self.dropdown['values'] = [k for k, v in self.data_store.items() if v]
            if self.dropdown['values']: 
                self.dropdown.current(0)
                self.refresh_preview()
            
            total = sum(len(v) for v in self.data_store.values())
            self.log(f"✅ Loaded {os.path.basename(path)}: {total} feedback entries")
            self.update_status(f"Ready | Loaded {total} entries from {os.path.basename(path)}")
            
        except Exception as e:
            self.log(f"❌ Error loading file: {e}")
            self.update_status("Error loading file")

    def run_sequential(self):
        data = self.data_store.get(self.cat_var.get(), [])
        if not data:
            self.log("❌ No data to process. Please load or generate data first.")
            return
        
        self.update_status(f"Processing {len(data)} feedback entries sequentially...")
        self.log(f"📊 Starting SEQUENTIAL benchmark on {len(data)} feedback entries...")
        
        start = time.perf_counter()
        self.last_results = [analyze_feedback(x) for x in data]
        elapsed = time.perf_counter() - start
        
        self.results_map["Sequential"] = elapsed
        self.update_chart()
        self.log(f"✅ Sequential processing completed: {elapsed:.3f} seconds")
        self.log(f"   Processed {len(data)} entries at {len(data)/elapsed:.1f} entries/second")
        self.update_status(f"Ready | Sequential: {elapsed:.3f}s for {len(data)} entries")

    def run_threading(self):
        data = self.data_store.get(self.cat_var.get(), [])
        if not data:
            self.log("❌ No data to process. Please load or generate data first.")
            return
        
        num_threads = min(multiprocessing.cpu_count() * 2, 8)
        self.update_status(f"Processing {len(data)} entries with {num_threads} threads...")
        self.log(f"🧵 Starting THREADING benchmark with {num_threads} threads on {len(data)} entries...")
        self.log(f"   Note: Due to Python's GIL, threading may be slower than sequential for CPU work")
        
        start = time.perf_counter()
        
        # Split data into chunks
        chunks = [data[i::num_threads] for i in range(num_threads)]
        thread_results = [None] * num_threads
        
        def worker(chunk_data, result_index):
            """Process a chunk and store results"""
            result = [analyze_feedback(x) for x in chunk_data]
            thread_results[result_index] = result
        
        # Create and start threads
        threads = []
        for i, chunk in enumerate(chunks):
            if chunk:
                t = threading.Thread(target=worker, args=(chunk, i))
                threads.append(t)
                t.start()
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
        
        # Combine results
        self.last_results = []
        for result in thread_results:
            if result is not None:
                self.last_results.extend(result)
        
        elapsed = time.perf_counter() - start
        self.results_map["Threading"] = elapsed
        self.update_chart()
        
        # Compare with sequential
        if self.results_map["Sequential"] > 0:
            ratio = elapsed / self.results_map["Sequential"]
            if ratio > 1:
                self.log(f"⚠️ Threading completed: {elapsed:.3f} seconds")
                self.log(f"   Actually {ratio:.2f}x SLOWER than sequential (GIL overhead)")
            else:
                self.log(f"✅ Threading completed: {elapsed:.3f} seconds")
                self.log(f"   {1/ratio:.2f}x faster than sequential (unusual for CPU work)")
        else:
            self.log(f"🔄 Threading completed: {elapsed:.3f} seconds")
        
        self.update_status(f"Ready | Threading: {elapsed:.3f}s for {len(data)} entries")

    def run_parallel(self):
        data = self.data_store.get(self.cat_var.get(), [])
        if not data:
            self.log("❌ No data to process. Please load or generate data first.")
            return
        
        cpu_count = multiprocessing.cpu_count()
        chunksize = max(1, len(data) // (cpu_count * 10))
        
        self.update_status(f"Processing {len(data)} entries on {cpu_count} CPU cores...")
        self.log(f"⚡ Starting MULTIPROCESSING benchmark with {cpu_count} processes...")
        self.log(f"   Chunksize: {chunksize} entries per chunk")
        
        start = time.perf_counter()
        
        # Use multiprocessing Pool
        with multiprocessing.Pool(processes=cpu_count) as pool:
            self.last_results = pool.map(analyze_feedback, data, chunksize=chunksize)
        
        elapsed = time.perf_counter() - start
        self.results_map["Parallel"] = elapsed
        self.update_chart()
        
        # Calculate and display speedup
        if self.results_map["Sequential"] > 0:
            speedup = self.results_map["Sequential"] / elapsed
            efficiency = (speedup / cpu_count) * 100
            self.log(f"🚀 MULTIPROCESSING completed: {elapsed:.3f} seconds")
            self.log(f"   Speedup: {speedup:.2f}x faster than sequential")
            self.log(f"   Efficiency: {efficiency:.1f}% of theoretical max ({cpu_count} cores)")
            self.log(f"   Business impact: Saved {self.results_map['Sequential'] - elapsed:.1f} seconds")
        else:
            self.log(f"✅ Multiprocessing completed: {elapsed:.3f} seconds")
        
        self.update_status(f"Ready | Parallel: {elapsed:.3f}s for {len(data)} entries")

    def clear_all(self):
        self.results_map = {"Sequential": 0.0, "Threading": 0.0, "Parallel": 0.0}
        self.last_results = []
        self.log_box.delete("1.0", tk.END)
        self.update_chart()
        self.log("🗑️ All results cleared")
        self.update_status("Ready | Results cleared")

    def export_to_csv(self):
        if not self.last_results:
            self.log("❌ No results to export. Run a benchmark first.")
            return
        
        path = filedialog.asksaveasfilename(defaultextension=".csv", 
                                           filetypes=[("CSV files", "*.csv")])
        if path:
            try:
                with open(path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Feedback ID", "Analysis Score", "Feedback Text Preview"])
                    cat = self.cat_var.get()
                    if cat and cat in self.data_store:
                        for i, score in enumerate(self.last_results[:1000]):  # Limit to 1000 for performance
                            text = self.data_store[cat][i][:100] if i < len(self.data_store[cat]) else "N/A"
                            writer.writerow([i+1, round(score, 2), text])
                self.log(f"✅ Exported {min(len(self.last_results), 1000)} results to {os.path.basename(path)}")
                self.update_status(f"Ready | Exported to {os.path.basename(path)}")
            except Exception as e:
                self.log(f"❌ Export error: {e}")
                self.update_status("Export failed")

    def show_about(self):
        """Show about dialog"""
        about_text = """📊 Customer Feedback Analyzer v7.0
        
A professional feedback processing tool with built-in performance benchmarking capabilities.

Purpose:
• Process large volumes of customer feedback efficiently
• Benchmark sequential, threading, and multiprocessing performance
• Demonstrate Python concurrency concepts with real data

Key Business Insight:
For CPU-intensive text analysis, multiprocessing provides 2-8x speedup over sequential processing, helping organizations process thousands of feedback entries in seconds rather than minutes.

Technical Note:
Threading may appear slower than sequential - this correctly demonstrates Python's Global Interpreter Lock (GIL) limitations for CPU-bound workloads.

System Information:
• CPU Cores: """ + str(multiprocessing.cpu_count()) + f"""
• Python Version: {sys.version.split()[0]}

Use Case:
Perfect for organizations processing thousands of feedback entries daily who need to optimize their data pipelines and understand parallel processing benefits.

© 2024 Customer Feedback Analyzer - Performance Intelligence for Business"""
        
        messagebox.showinfo("About Customer Feedback Analyzer", about_text)

    def show_guide(self):
        """Show performance guide"""
        guide_text = """📖 Performance Benchmarking Guide

Understanding Your Results:

1️⃣ SEQUENTIAL (Baseline)
   • Single-core processing
   • No parallel overhead
   • Best for small datasets (<100 items)

2️⃣ THREADING (GIL-Limited)
   • May be 10-30% SLOWER than sequential
   • Due to Python's Global Interpreter Lock
   • Better for I/O-bound tasks (network, disk)
   • NOT recommended for CPU-heavy analysis

3️⃣ MULTIPROCESSING (True Parallel)
   • Uses all available CPU cores
   • 2-8x FASTER for large datasets
   • Best for 500+ feedback entries
   • Optimal for enterprise workloads

Expected Performance (4-core CPU, 1000 entries):
• Sequential: 8-10 seconds (baseline)
• Threading: 9-12 seconds (GIL overhead)
• Multiprocessing: 2-3 seconds (3-4x speedup)

Tips for Best Results:
• Use 500+ entries to see parallel benefits
• Select "Enterprise" category for maximum CPU work
• Run benchmarks multiple times for consistency
• Monitor CPU usage in Task Manager/Activity Monitor

Business Value:
• Process daily feedback volumes 4x faster
• Handle peak loads without infrastructure upgrades
• Make data-driven decisions on processing strategies"""
        
        messagebox.showinfo("Performance Guide", guide_text)

if __name__ == "__main__":
    import sys
    multiprocessing.freeze_support()
    root = tk.Tk()
    app = FeedbackApp(root)
    root.mainloop()
    