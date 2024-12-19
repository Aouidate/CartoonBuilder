import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import io

st.set_page_config(layout="wide")

@dataclass
class MolecularComponent:
    name: str
    shape: str
    color: str
    label: str

@dataclass
class AttachmentPoint:
    name: str
    position: Tuple[float, float]

@dataclass
class Molecule:
    scaffold: MolecularComponent
    attachment_points: Dict[str, AttachmentPoint]
    attached_sugars: Dict[str, List[MolecularComponent]]
    attached_substituents: Dict[str, List[MolecularComponent]]

class MoleculeBuilder:
    def __init__(self):
        self.scaffolds = {
            'QA': MolecularComponent('QA', 'hexagon', 'lime', 'QA'),
            'QA-OH': MolecularComponent('QA', 'hexagon', 'limegreen', 'QA-OH'),
            'BA': MolecularComponent('BA', 'hexagon', 'red', 'BA'),
            'P': MolecularComponent('BA', 'hexagon', 'gray', 'P'),
            'P-Ac': MolecularComponent('BA', 'hexagon', 'gainsboro', 'P-Ac'),
            'G': MolecularComponent('BA', 'hexagon', 'magenta', 'G'),
            'E': MolecularComponent('BA', 'hexagon', 'goldenrod', 'E'),
            'E-A': MolecularComponent('BA', 'hexagon', 'gold', 'E-A'),

        }
        self.sugars = {
            'XYL': MolecularComponent('XYL', 'circle', '#228B22', 'Xyl'),
            'FUC': MolecularComponent('FUC', 'circle', '#DC143C', 'Fuc'),
            'GLU': MolecularComponent('GLU', 'circle', '#9370DB', 'Glu'),
            'RHA': MolecularComponent('RHA', 'circle', '#FFD700', 'Rha'),
            'ARA': MolecularComponent('RHA', 'circle', 'cyan', 'Ara'),
            'GAL': MolecularComponent('RHA', 'circle', 'orange', 'Gal'),
        }
        self.substituents = {
            'H': MolecularComponent('H', 'circle', 'none', 'H'),
            'Acyl': MolecularComponent('Acyl', 'circle', 'none', 'Ac'),
            'OH': MolecularComponent('OH', 'circle', 'none', 'OH'),
            'OHMeHex': MolecularComponent('OHMeHex', 'circle', 'none', 'OHMeHex')
        }
        self.attachment_points = {
            'Zero': AttachmentPoint('Zero', (0, 0)),
            'FRight': AttachmentPoint('FR', (1, 0)),
            'FLeft': AttachmentPoint('FL', (-1, 0)),
            'SRight': AttachmentPoint('FR', (2, 0)),
            'SLeft': AttachmentPoint('FL', (-2, 0)),
        }
        self.molecule = Molecule(
            scaffold=self.scaffolds['QA'],
            attachment_points=self.attachment_points,
            attached_sugars={},
            attached_substituents={}
        )
    def add_attachment_point(self, name: str, position: Tuple[float, float]):
        if name in self.attachment_points:
            raise ValueError(f"Attachment point '{name}' already exists.")
        self.attachment_points[name] = AttachmentPoint(name, position)

    def add_component(self, name: str, shape: str, color: str, label: str, category: str):
        VALID_SHAPES = ['hexagon', 'circle']
        if shape not in VALID_SHAPES:
            raise ValueError(f"Invalid shape: {shape}. Valid options are {VALID_SHAPES}.")
        try:
            plt.plot(c=color)  # Matplotlib-compatible color validation
        except ValueError:
            raise ValueError(f"Invalid color value: {color}. Please provide a valid hex or named color.")
        
        component = MolecularComponent(name, shape, color, label)
        if category == "Sugar":
            self.sugars[name] = component
        elif category == "Substituent":
            self.substituents[name] = component
        elif category == "Scaffold":
            self.scaffolds[name] = component

    def attach_component(self, parent_point: str, component_name: str, direction: str, category: str):
        if parent_point not in self.attachment_points:
            raise ValueError(f"Invalid attachment point: {parent_point}")

        component = self.sugars.get(component_name) if category == "Sugar" else self.substituents.get(component_name)
        if not component:
            raise ValueError(f"Component '{component_name}' does not exist in category '{category}'.")

        # Ensure components are stored as tuples with direction
        if category == "Sugar":
            if parent_point not in self.molecule.attached_sugars:
                self.molecule.attached_sugars[parent_point] = []
            self.molecule.attached_sugars[parent_point].append((component, direction))  # Always store tuples
        else:
            if parent_point not in self.molecule.attached_substituents:
                self.molecule.attached_substituents[parent_point] = []
            self.molecule.attached_substituents[parent_point].append((component, direction))  # Always store tuples

    def draw_shape(self, shape_type: str, ax: plt.Axes, position: Tuple[float, float], color: str, label: str):
        if shape_type == 'hexagon':
            # Adjusting for center position
            width = height = 0.1  # Total width and height of the shape 
            rect = FancyBboxPatch(
                #(position[0]-0.5, position[1]-0.5),
                (position[0] - width / 2, position[1] - height / 2), 
                width, height,
                boxstyle="round,pad=0.6,rounding_size=0.0",
                edgecolor="black",
                linewidth=2,
                facecolor=color,
                alpha=1.0
            )
            ax.add_patch(rect)
            ax.text(position[0], position[1], label, ha='center', va='center', fontweight='bold', fontsize=13)
        elif shape_type == 'circle':
            circle = plt.Circle(position, 0.5, facecolor=color, alpha=1.0,  edgecolor='black', linewidth=2)
            ax.add_artist(circle)
            ax.text(position[0], position[1], label, ha='center', va='center', fontweight='bold', fontsize=8)


    def visualize_molecule(self):
        #fig_width = max(10, 2 * (len(self.molecule.attached_sugars) + len(self.molecule.attached_substituents)))
        fig, ax = plt.subplots(#figsize=(fig_width, fig_width)) 
         ) # Dynamically scale the figure width

        #all_positions = [(0, 0)]  # Start with the scaffold position at (0, 0)
        fig, ax = plt.subplots(figsize=(10, 4))

        # Draw scaffold
        scaffold_pos = (0, 0)
        scaffold = self.molecule.scaffold  # Access scaffold from the molecule
        self.draw_shape(scaffold.shape, ax, scaffold_pos, scaffold.color, scaffold.label)

        # List to store all positions for dynamic axis limits
        all_positions = [scaffold_pos]  # Start with the scaffold position

        # Draw attached sugars
        for point, sugars in self.molecule.attached_sugars.items():
            base_position = (
                scaffold_pos[0],#+ float(self.attachment_points[point].position[0]),
                scaffold_pos[1]# + float(self.attachment_points[point].position[1])
            )
            for i, (component, direction) in enumerate(sugars):
                direction_vector = {
                     "Right": (1, 0),
                    "Left": (-1, 0),
                    "Up": (0, 1),
                    "Down": (0, -1),  
                }.get(direction, (1, 0))  # Default to "Right"
                component_position = (
                    self.attachment_points[point].position[0] + direction_vector[0] * 1.0, #* (i + 1) * 1,
                    self.attachment_points[point].position[1] + direction_vector[1] * 1.0 #* (i + 1) * 1
                )
                all_positions.append(component_position)

                # Draw the component
                self.draw_shape(component.shape, ax, component_position, component.color, component.label)

        # Draw attached substituents
        for point, substituents in self.molecule.attached_substituents.items():
            base_position = (
                scaffold_pos[0], #+ float(self.attachment_points[point].position[0]),
                scaffold_pos[1] #+ float(self.attachment_points[point].position[1])
            )
            for i, (component, direction) in enumerate(substituents):
                direction_vector = {
                    "Right": (1, 0),
                    "Left": (-1, 0),
                    "Up": (0, 1),
                    "Down": (0, -1),    
                }.get(direction, (1, 0))  # Default to "Right"
                component_position = (
                    self.attachment_points[point].position[0] + direction_vector[0] * 1.0, #* (i + 1) * 1.2,
                    self.attachment_points[point].position[1] + direction_vector[1] * 1.0 #* (i + 1) * 1.2
                )
                all_positions.append(component_position)

                # Draw the component
                self.draw_shape(component.shape, ax, component_position, component.color, component.label)

        buffer = 7  # Add a buffer around all components
        ax.set_xlim(-buffer, buffer)
        ax.set_ylim(-buffer, buffer)
        ax.set_aspect('equal', adjustable='datalim')  # Ensure equal scaling

        # Turn off axis
        ax.axis('off')
        #ax.grid(True)  # Optional: Add light grid lines for alignment

        plt.tight_layout()  # Ensure no clipping
        return fig


        # # Dynamically set axis limits based on scaffold and attached component positions
        # x_positions, y_positions = zip(*all_positions)
        # ax.set_xlim(min(x_positions) - 1, max(x_positions) + 1)
        # ax.set_ylim(min(y_positions) - 1, max(y_positions) + 1)

        # ax.set_aspect('equal', adjustable='datalim')  # Ensure equal scaling
        # plt.show()
        # return fig

    
    def _draw_attached_components(self, ax, scaffold_pos, point, components):
        # Define direction vectors for placement
        DIRECTION_VECTORS = {
            "Up": (0, 1),
            "Down": (0, -1),
            "Left": (-1, 0),
            "Right": (1, 0)
        }
        
        # Base position for the attachment point
        base_position = (
            scaffold_pos[0] + float(self.attachment_points[point].position[0]),
            scaffold_pos[1] + float(self.attachment_points[point].position[1])
        )

        # Default offset for line adjustment
        OFFSET = 0.5

        # Iterate over components attached at the given point
        for i, (component, direction) in enumerate(components):
            # Get the direction vector; default to "Right" if none provided
            direction_vector = DIRECTION_VECTORS.get(direction, DIRECTION_VECTORS["Right"])
            
            # Calculate the start and end points of the line
            line_start = (
                base_position[0] + direction_vector[0] * OFFSET,  # Offset from the attachment point
                base_position[1] + direction_vector[1] * OFFSET
            )
            line_end = (
                base_position[0] + direction_vector[0] * (i + 1) * 1.2 - direction_vector[0] * OFFSET,
                base_position[1] + direction_vector[1] * (i + 1) * 1.2 - direction_vector[1] * OFFSET
            )

            # Draw the line connecting the scaffold to the component
            ax.plot(
                [line_start[0], line_end[0]],
                [line_start[1], line_end[1]],
                'k-', zorder=1  # zorder ensures the line is drawn beneath shapes
            )

            # Calculate the position of the attached component
            component_position = (
                base_position[0] + direction_vector[0] * (i + 1) * 1.2,
                base_position[1] + direction_vector[1] * (i + 1) * 1.2
            )

            # Draw the attached component shape at its position
            self.draw_shape(component.shape, ax, component_position, component.color, component.label)




def main():
    st.markdown("<h1 style='text-align:center;'>👨🏽‍💻Saponins Builder</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:gray; text-align:center; font-size:18px;'>📝 Tip: Start by selecting a scaffold and then attach components like sugars or substituents using the tools below.</p>", unsafe_allow_html=True)
    if 'builder' not in st.session_state:
        st.session_state.builder = MoleculeBuilder()

    builder = st.session_state.builder

    col1, col2 = st.columns([1.0, 4.5])  # Allocate more space to the visual output

    with col1:
        st.markdown("<h3 style='text-align: center;'> 🧰 Build Your Molecule </h3>", unsafe_allow_html=True)
        #st.subheader("Build Your Molecule")

        with st.expander("Add New Component"):
            name = st.text_input("Name")
            label = st.text_input("Label")
            shape = st.selectbox("Shape", ["hexagon", "circle"])
            color = st.color_picker("Color")
            category = st.selectbox("Category", ["Scaffold", "Sugar", "Substituent"])

            if st.button("Add Component"):
                if name and label:
                    builder.add_component(name, shape, color, label, category)
                    st.success(f"Added {category}: {name}")
                else:
                    st.error("Name and label are required.")

        # with st.write("### Existing Components"):
        #     component_data = [
        #         {"Name": component.name, "Label": component.label, "Shape": component.shape, "Color": component.color}
        #         for component in list(builder.sugars.values()) + list(builder.substituents.values())
        #     ]
        #     st.table(component_data)

        with st.expander("Select Scaffold"):
            scaffold = st.selectbox("Scaffold", list(builder.scaffolds.keys()))
            builder.molecule.scaffold = builder.scaffolds[scaffold]
            st.success(f"Selected scaffold: {scaffold}")

        with st.expander("Add New Attachment Point"):
            point_name = st.text_input("Attachment Point Name")
            x = st.number_input("X Coordinate", value=0.0, step=1.0)
            y = st.number_input("Y Coordinate", value=0.0, step=1.0)
            
            if st.button("Add Attachment Point"):
                try:
                    builder.add_attachment_point(point_name, (x, y))
                    st.success(f"Added attachment point: {point_name}")
                except ValueError as e:
                    st.error(str(e))


        with st.expander("Attach Component"):
            point = st.selectbox("Attachment Point", list(builder.attachment_points.keys()))
            category = st.selectbox("Category", ["Sugar", "Substituent"])
            component = st.selectbox(
                "Component",
                list(builder.sugars.keys() if category == "Sugar" else builder.substituents.keys())
            )
            direction = st.selectbox("Direction", ["Up", "Down", "Left", "Right"])

            if st.button("Attach Component"):
                try:
                    builder.attach_component(point, component, direction, category)
                    st.success(f"Attached {category}: {component} to {point}")
                except ValueError as e:
                    st.error(str(e))

    with col2:
        #st.subheader("Visualization")
        fig = builder.visualize_molecule()
        if fig:
            buf = io.BytesIO()
            fig.savefig(buf, format="png",  bbox_inches='tight')
            buf.seek(0)
            st.image(buf, use_column_width=True
                     )
            st.download_button( label="Download image",
            data=buf,
            file_name="Saponin.png",
            mime="image/png",
            use_container_width = True,
            )
if __name__ == "__main__":
    main()