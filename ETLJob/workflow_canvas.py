"""
Workflow Canvas - Visual drag-and-drop workflow designer
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math


class WorkflowCanvas:
    """Visual workflow designer with drag-and-drop"""
    
    def __init__(self, parent, job_manager):
        self.parent = parent
        self.job_manager = job_manager
        self.jobs = {}
        self.job_positions = {}
        self.selected_job = None
        self.dragging = False
        self.drag_start = None
        
        self.setup_ui()
        self.load_jobs()
        
    def setup_ui(self):
        """Setup workflow canvas UI"""
        # Toolbar
        toolbar = ttk.Frame(self.parent)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Auto Layout", command=self.auto_layout).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Refresh", command=self.refresh).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Zoom In", command=self.zoom_in).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Zoom Out", command=self.zoom_out).pack(side=tk.LEFT, padx=5)
        ttk.Label(toolbar, text="Double-click a job to edit").pack(side=tk.RIGHT, padx=10)
        
        # Canvas with scrollbars
        canvas_frame = ttk.Frame(self.parent)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(canvas_frame, bg="white", width=1000, height=600)
        
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Set up canvas scrolling region
        self.canvas.configure(scrollregion=(0, 0, 2000, 2000))
        
        # Bind events
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        
        # Legend
        legend_frame = ttk.LabelFrame(self.parent, text="Legend", padding=10)
        legend_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(legend_frame, text="● Running", foreground="orange").pack(side=tk.LEFT, padx=10)
        ttk.Label(legend_frame, text="● Completed", foreground="green").pack(side=tk.LEFT, padx=10)
        ttk.Label(legend_frame, text="● Failed", foreground="red").pack(side=tk.LEFT, padx=10)
        ttk.Label(legend_frame, text="● Idle", foreground="blue").pack(side=tk.LEFT, padx=10)
        ttk.Label(legend_frame, text="→ Dependency", foreground="gray").pack(side=tk.LEFT, padx=10)
        
    def load_jobs(self):
        """Load jobs from database"""
        self.jobs = {job['id']: job for job in self.job_manager.get_all_jobs()}
        self.auto_layout()
        
    def refresh(self):
        """Refresh the workflow display"""
        self.load_jobs()
        
    def auto_layout(self):
        """Automatically layout jobs"""
        if not self.jobs:
            return
            
        # Build dependency graph
        graph = {}
        in_degree = {}
        
        for job_id in self.jobs:
            graph[job_id] = []
            in_degree[job_id] = 0
            
        for job_id in self.jobs:
            deps = self.job_manager.get_job_dependencies(job_id)
            for dep in deps:
                graph[dep['depends_on_job_id']].append(job_id)
                in_degree[job_id] += 1
                
        # Topological sort to determine levels
        levels = {}
        queue = [job_id for job_id in self.jobs if in_degree[job_id] == 0]
        current_level = 0
        
        while queue:
            next_queue = []
            for job_id in queue:
                levels[job_id] = current_level
                for dependent in graph[job_id]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        next_queue.append(dependent)
            queue = next_queue
            current_level += 1
            
        # Position jobs based on levels
        level_counts = {}
        for job_id, level in levels.items():
            level_counts[level] = level_counts.get(level, 0) + 1
            
        level_positions = {level: 0 for level in level_counts}
        
        x_spacing = 200
        y_spacing = 120
        start_x = 100
        start_y = 100
        
        self.job_positions = {}
        for job_id, level in sorted(levels.items(), key=lambda x: (x[1], x[0])):
            x = start_x + level * x_spacing
            y = start_y + level_positions[level] * y_spacing
            self.job_positions[job_id] = (x, y)
            level_positions[level] += 1
            
        self.draw_workflow()
        
    def draw_workflow(self):
        """Draw the workflow on canvas"""
        self.canvas.delete("all")
        
        # Draw dependency arrows first (so they're behind jobs)
        for job_id in self.jobs:
            if job_id in self.job_positions:
                deps = self.job_manager.get_job_dependencies(job_id)
                for dep in deps:
                    dep_id = dep['depends_on_job_id']
                    if dep_id in self.job_positions:
                        x1, y1 = self.job_positions[dep_id]
                        x2, y2 = self.job_positions[job_id]
                        
                        # Draw arrow
                        self.canvas.create_line(
                            x1 + 60, y1 + 20, x2, y2 + 20,
                            arrow=tk.LAST,
                            fill="gray",
                            width=2,
                            tags="arrow"
                        )
                        
        # Draw jobs
        for job_id, job in self.jobs.items():
            if job_id in self.job_positions:
                x, y = self.job_positions[job_id]
                self.draw_job(job_id, job, x, y)
                
    def draw_job(self, job_id, job, x, y):
        """Draw a single job box"""
        width = 120
        height = 40
        
        # Determine color based on status
        status = job['status']
        if status == 'running':
            color = "orange"
        elif status == 'completed':
            color = "lightgreen"
        elif status == 'failed':
            color = "lightcoral"
        else:
            color = "lightblue"
            
        # Draw box
        box = self.canvas.create_rectangle(
            x, y, x + width, y + height,
            fill=color,
            outline="black",
            width=2,
            tags=f"job_{job_id}"
        )
        
        # Draw enabled indicator
        if not job['enabled']:
            self.canvas.create_text(
                x + 10, y + 10,
                text="⏸",
                font=("Arial", 12),
                anchor=tk.NW,
                tags=f"job_{job_id}"
            )
            
        # Draw job name
        name = job['name']
        if len(name) > 15:
            name = name[:12] + "..."
            
        self.canvas.create_text(
            x + width / 2, y + height / 2,
            text=name,
            font=("Arial", 10, "bold"),
            tags=f"job_{job_id}"
        )
        
        # Draw job type indicator
        type_icon = {"python": "🐍", "shell": "💻", "sql": "📊"}.get(job['job_type'], "")
        self.canvas.create_text(
            x + width - 15, y + 10,
            text=type_icon,
            font=("Arial", 12),
            anchor=tk.NE,
            tags=f"job_{job_id}"
        )
        
    def on_mouse_down(self, event):
        """Handle mouse down event"""
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Find clicked job
        items = self.canvas.find_overlapping(canvas_x - 2, canvas_y - 2, canvas_x + 2, canvas_y + 2)
        for item in items:
            tags = self.canvas.gettags(item)
            for tag in tags:
                if tag.startswith("job_"):
                    job_id = int(tag.split("_")[1])
                    self.selected_job = job_id
                    self.dragging = True
                    self.drag_start = (canvas_x, canvas_y)
                    return
                    
    def on_mouse_move(self, event):
        """Handle mouse move event"""
        if self.dragging and self.selected_job:
            canvas_x = self.canvas.canvasx(event.x)
            canvas_y = self.canvas.canvasy(event.y)
            
            dx = canvas_x - self.drag_start[0]
            dy = canvas_y - self.drag_start[1]
            
            # Move job
            old_x, old_y = self.job_positions[self.selected_job]
            self.job_positions[self.selected_job] = (old_x + dx, old_y + dy)
            
            self.drag_start = (canvas_x, canvas_y)
            self.draw_workflow()
            
    def on_mouse_up(self, event):
        """Handle mouse up event"""
        self.dragging = False
        self.drag_start = None
        
    def on_double_click(self, event):
        """Handle double click event"""
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Find clicked job
        items = self.canvas.find_overlapping(canvas_x - 2, canvas_y - 2, canvas_x + 2, canvas_y + 2)
        for item in items:
            tags = self.canvas.gettags(item)
            for tag in tags:
                if tag.startswith("job_"):
                    job_id = int(tag.split("_")[1])
                    self.edit_job(job_id)
                    return
                    
    def edit_job(self, job_id):
        """Open job edit dialog"""
        messagebox.showinfo("Edit Job", f"Would open edit dialog for job {self.jobs[job_id]['name']}")
        
    def zoom_in(self):
        """Zoom in on canvas"""
        self.canvas.scale("all", 0, 0, 1.2, 1.2)
        
    def zoom_out(self):
        """Zoom out on canvas"""
        self.canvas.scale("all", 0, 0, 0.8, 0.8)