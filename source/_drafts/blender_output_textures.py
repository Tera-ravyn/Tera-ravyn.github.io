import os
import bpy
from bpy.path import abspath, relpath
from bpy.props import (StringProperty, 
                      BoolProperty, 
                      EnumProperty,
                      CollectionProperty)
from bpy.types import (Operator, 
                       Panel, 
                       PropertyGroup,
                       UIList)
from bpy.utils import register_class, unregister_class

# 工具函数：获取节点树的原始贴图尺寸
def get_original_texture_size(node):
    """递归查找连接的原始贴图尺寸"""
    if node.bl_idname == 'ShaderNodeTexImage' and node.image:
        return node.image.size
    for input in node.inputs:
        if input.is_linked:
            linked_node = input.links[0].from_node
            size = get_original_texture_size(linked_node)
            if size:
                return size
    return None

# 工具函数：导出节点内容
def export_node(node, output_path, size=(1024, 1024)):
    """临时渲染节点到指定尺寸的图片"""
    # 创建临时渲染场景
    scene = bpy.context.scene
    original_tree = scene.node_tree
    scene.use_nodes = True
    temp_tree = scene.node_tree
    
    # 设置合成节点
    render_layer = temp_tree.nodes.new('CompositorNodeRLayers')
    composite = temp_tree.nodes.new('CompositorNodeComposite')
    viewer = temp_tree.nodes.new('CompositorNodeViewer')
    
    # 复制目标节点到临时树
    temp_node = temp_tree.nodes.new(node.bl_idname)
    for prop in node.bl_rna.properties:
        if not prop.is_readonly:
            try:
                setattr(temp_node, prop.identifier, getattr(node, prop.identifier))
            except:
                pass
    
    # 连接节点
    temp_tree.links.new(temp_node.outputs[0], viewer.inputs[0])
    
    # 设置渲染尺寸
    scene.render.resolution_x = size[0]
    scene.render.resolution_y = size[1]
    
    # 渲染并保存
    bpy.ops.render.render()
    if viewer.image:
        viewer.image.save_render(output_path)
    
    # 恢复原始设置
    scene.node_tree = original_tree
    bpy.data.node_groups.remove(temp_tree)

def export_node_to_pixels(node, size=(1024, 1024)):
    """
    将节点渲染为一维像素数组（每个值代表灰度或强度）
    返回值: List[float]，长度为 width * height
    """
    width, height = size
    temp_img_path = os.path.join(os.getenv("TEMP"), f"temp_export_{os.urandom(4).hex()}.png")

    # 使用现有 export_node 函数先渲染成图像
    export_node(node, temp_img_path, size)

    # 加载图像并转换为灰度
    from PIL import Image
    img = Image.open(temp_img_path).convert('L')
    pixels = list(img.getdata())

    # 归一化到 [0.0, 1.0]
    normalized = [p / 255.0 for p in pixels]

    # 删除临时文件
    os.remove(temp_img_path)

    return normalized

# 主导出逻辑
def export_material(material, output_dir, create_subfolder=True):
    """导出单个材质的所有贴图"""
    if not material.use_nodes:
        return None
    
    # 创建材质专属文件夹
    mat_dir = os.path.join(output_dir, material.name) if create_subfolder else output_dir
    os.makedirs(mat_dir, exist_ok=True)
    
    bsdf = next((n for n in material.node_tree.nodes if n.bl_idname == 'ShaderNodeBsdfPrincipled'), None)
    if not bsdf:
        return None
    
    exported_textures = {}

    metallic = bsdf.inputs.get('Metallic')
    roughness = bsdf.inputs.get('Roughness')
    if metallic and roughness and metallic.is_linked and roughness.is_linked:
        metallic_node = metallic.links[0].from_node
        roughness_node = roughness.links[0].from_node

        # 获取图像尺寸
        size = get_original_texture_size(metallic_node) or (1024, 1024)
        width, height = size

        # 创建内存图像
        img = bpy.data.images.new(
            name=f"{material.name}_RoughnessMetallic",
            width=width,
            height=height,
            alpha=True
        )

        # 渲染 metallic 和 roughness 节点成图像数据（调用 export_node_to_pixels）
        metallic_pixels = export_node_to_pixels(metallic_node, size)
        roughness_pixels = export_node_to_pixels(roughness_node, size)

        # 合并像素数据：R=0, G=Roughness, B=Metallic, A=1.0
        combined_pixels = []
        for i in range(width * height):
            m = metallic_pixels[i]
            r = roughness_pixels[i]
            combined_pixels.extend([0.0, r, m, 1.0])  # RGBA

        # 写入图像
        img.pixels = combined_pixels

        # 保存图像
        output_path = os.path.join(mat_dir, f"{material.name}_RoughnessMetallic.png")
        img.file_format = 'PNG'
        img.save_render(output_path)

        # 清理
        bpy.data.images.remove(img)

        exported_textures["RoughnessMetallic"] = output_path
    
    # 导出其他贴图
    for socket_name in ['Base Color', 'Normal']:
        socket = bsdf.inputs.get(socket_name)
        if not socket:
            continue
        
        # 获取连接的节点
        linked_node = socket.links[0].from_node if socket.is_linked else None
        
        # 处理法线贴图特殊逻辑
        if socket_name == 'Normal' and linked_node and linked_node.bl_idname == 'ShaderNodeNormalMap':
            linked_node = linked_node.inputs['Color'].links[0].from_node if linked_node.inputs['Color'].is_linked else None

        if linked_node:
            # 自动检测原始贴图尺寸
            original_size = get_original_texture_size(linked_node) or (1024, 1024)
            
            output_path = os.path.join(mat_dir, f"{material.name}_{socket_name.replace(' ', '_')}.png")
            export_node(linked_node, output_path, original_size)
            exported_textures[socket_name] = output_path
        elif hasattr(socket, 'default_value'):
            # 导出纯色
            output_path = os.path.join(mat_dir, f"{material.name}_{socket_name.replace(' ', '_')}_Color.png")
            color = socket.default_value[:3] if hasattr(socket.default_value, '__len__') else (socket.default_value,) * 3
            img = bpy.data.images.new(
                f"{material.name}_{socket_name}_Color",
                width=1024,
                height=1024,
            )
            img.pixels = [*color, 1.0] * (1024 * 1024)
            img.file_format = 'PNG'
            img.save_render(output_path)
            bpy.data.images.remove(img)
            exported_textures[socket_name] = output_path
    
    return exported_textures

# 生成VRM材质
def create_vrm_material(original_mat, textures, output_dir):
    """创建符合VRM标准的材质"""
    vrm_mat = bpy.data.materials.new(f"VRM_{original_mat.name}")
    vrm_mat.use_nodes = True
    
    nodes = vrm_mat.node_tree.nodes
    links = vrm_mat.node_tree.links
    
    # 清除默认节点
    for node in nodes:
        nodes.remove(node)
    
    # 创建VRM标准节点树
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 300)
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (500, 300)
    links.new(bsdf.outputs[0], output.inputs[0])
    
    # 连接贴图
    if 'Base Color' in textures:
        tex = nodes.new('ShaderNodeTexImage')
        tex.image = bpy.data.images.load(textures['Base Color'])
        tex.location = (0, 400)
        links.new(tex.outputs[0], bsdf.inputs['Base Color'])
    
    if 'Normal' in textures:
        tex = nodes.new('ShaderNodeTexImage')
        tex.image = bpy.data.images.load(textures['Normal'])
        tex.location = (0, 100)
        normal_map = nodes.new('ShaderNodeNormalMap')
        normal_map.location = (200, 100)
        links.new(tex.outputs[0], normal_map.inputs['Color'])
        links.new(normal_map.outputs[0], bsdf.inputs['Normal'])
    
    if 'RoughnessMetallic' in textures:
        tex = nodes.new('ShaderNodeTexImage')
        tex.image = bpy.data.images.load(textures['RoughnessMetallic'])
        tex.location = (0, 0)
        separate_node = nodes.new('ShaderNodeSeparateRGB')
        separate_node.location = (-200, 0)
        links.new(tex.outputs['Color'], separate_node.inputs['Image'])
        links.new(separate_node.outputs['B'], bsdf.inputs['Metallic'])
        links.new(separate_node.outputs['G'], bsdf.inputs['Roughness'])

    return vrm_mat

def update_directory(self, context):
    if self.directory:
        self.directory = abspath(self.directory)

# 操作符主类
class BatchExportMaterials(Operator):
    bl_idname = "object.batch_export_materials"
    bl_label = "批量导出材质贴图"

    directory: StringProperty(
        subtype='DIR_PATH',
        update=update_directory
    )
    create_subfolders: BoolProperty(
        name="按材质分类",
        description="每个材质的贴图存入独立文件夹",
        default=True
    )
    generate_vrm: BoolProperty(
        name="生成VRM材质",
        description="创建符合VRM标准的新材质并替换",
        default=True
    )
    
    def execute(self, context):
        if not self.directory:
            self.report({'ERROR'}, "必须选择输出目录")
            return {'CANCELLED'}
        
        exported_materials = {}

        # 选择导出材质列表
        selected_materials = [
            item.pointer for item in context.scene.material_list 
            if item.selected
        ]
        
        if not selected_materials:
            self.report({'ERROR'}, "未选择任何材质")
            return {'CANCELLED'}
        
        # 导出选中材质
        exported_count = 0
        for mat in selected_materials:
            textures = export_material(mat, self.directory, self.create_subfolders)
            if textures:
                exported_materials[mat] = textures
                # print(f"已导出材质: {mat.name}")
                exported_count += 1

        # 生成VRM材质
        if self.generate_vrm:
            for original_mat, textures in exported_materials.items():
                vrm_mat = create_vrm_material(original_mat, textures, self.directory)
                
                # 替换场景中的材质引用
                for obj in bpy.data.objects:
                    for i, slot in enumerate(obj.material_slots):
                        if slot.material == original_mat:
                            slot.material = vrm_mat
        
        self.report({'INFO'}, f"成功导出 {len(exported_materials)} 个材质")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        # 初始化材质列表
        context.scene.material_list.clear()
        for mat in bpy.data.materials:
            item = context.scene.material_list.add()
            item.name = mat.name
            item.pointer = mat
        
        # 弹出窗口
        return context.window_manager.invoke_props_dialog(self, width=600)
    
    def draw(self, context):
        layout = self.layout
        
        # 材质选择列表
        box = layout.box()
        box.label(text="选择要导出的材质:")
        row = box.row()
        row.template_list(
            "MATERIAL_UL_List", "", 
            context.scene, "material_list",
            context.scene, "material_list_index",
            rows=8
        )
        
        # 操作按钮
        row = box.row()
        row.operator("material.select_all", text="全选").action = 'SELECT'
        row.operator("material.select_all", text="取消全选").action = 'DESELECT'
        
        # 导出选项
        layout.separator()
        layout.prop(self, "directory")
        layout.prop(self, "create_subfolders")
        layout.prop(self, "combine_mr")
        layout.prop(self, "generate_vrm")

# UI面板
class MATERIAL_PT_BatchExportPanel(Panel):
    bl_label = "材质批量导出"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("object.batch_export_materials")

# 材质选择项数据结构
class MaterialItem(PropertyGroup):
    selected: BoolProperty(name="选择", default=True)
    name: StringProperty(name="材质名称")
    pointer: bpy.props.PointerProperty(type=bpy.types.Material)

# 材质列表UI
class MATERIAL_UL_List(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row(align=True)
        row.prop(item, "selected", text="")
        row.label(text=item.name, icon='MATERIAL')

# 全选/取消全选操作
class SelectMaterials(Operator):
    bl_idname = "material.select_all"
    bl_label = "选择所有材质"
    
    action: EnumProperty(
        items=[
            ('SELECT', "全选", ""),
            ('DESELECT', "取消全选", "")
        ]
    )
    
    def execute(self, context):
        for item in context.scene.material_list:
            item.selected = (self.action == 'SELECT')
        return {'FINISHED'}

# 注册属性
def register():
    register_class(MaterialItem)
    bpy.types.Scene.material_list = CollectionProperty(type=MaterialItem)
    bpy.types.Scene.material_list_index = bpy.props.IntProperty()
    
    for cls in (
        MATERIAL_UL_List,
        SelectMaterials,
        BatchExportMaterials,
        MATERIAL_PT_BatchExportPanel
    ):
        register_class(cls)

def unregister():
    del bpy.types.Scene.material_list
    del bpy.types.Scene.material_list_index
    
    for cls in (
        MATERIAL_PT_BatchExportPanel,
        BatchExportMaterials,
        SelectMaterials,
        MATERIAL_UL_List,
        MaterialItem
    ):
        unregister_class(cls)

if __name__ == "__main__":
    register()
    bpy.ops.object.batch_export_materials('INVOKE_DEFAULT')