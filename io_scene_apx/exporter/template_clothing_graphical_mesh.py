templateGraphicalMesh = '''<value type="Ref" included="1" className="ClothingGraphicalLodParameters" version="0.4" checksum="0x8cf41087 0x1ec73f2e 0x602ad91d 0xdbec5061">      
        <struct name="">
          <array name="platforms" size="0" type="String"></array>
          <value name="lod" type="U32">{numLod}</value>
          <value name="physicalMeshId" type="U32">{physicalMeshId}</value>
          <value name="renderMeshAsset" type="Ref" included="1" className="RenderMeshAssetParameters" version="0.0" checksum="0x119d6f62 0x8d1ff03d 0x19864d20 0x93421fd0">          
	        <struct name="">
	          <array name="submeshes" size="{numSubMeshes}" type="Ref">
		        {subMeshes}
	          </array>
	          <array name="materialNames" size="{numSubMeshes}" type="String">
		        {materials}
	          </array>
	          <array name="partBounds" size="1" type="Bounds3">
		        {partBounds}
	          </array>
	          <value name="textureUVOrigin" type="U32">2</value>
	          <value name="boneCount" type="U32">{numUsedBones}</value>
	          <value name="deleteStaticBuffersAfterUse" type="Bool">false</value>
	          <value name="isReferenced" type="Bool">true</value>
	        </struct>
          </value>
          <array name="immediateClothMap" size="{numImmediateClothMap}" type="U32">
            {immediateClothMap}
          </array>
          <array name="skinClothMapB" size="0" type="Struct" structElements="vtxTetraBary(Vec3),vertexIndexPlusOffset(U32),nrmTetraBary(Vec3),faceIndex0(U32),tetraIndex(U32)"></array>
          <array name="skinClothMap" size="{numSkinClothMap}" type="Struct" structElements="vertexBary(Vec3),vertexIndex0(U32),normalBary(Vec3),vertexIndex1(U32),tangentBary(Vec3),vertexIndex2(U32),vertexIndexPlusOffset(U32)">
            {skinClothMap}
          </array>
          <value name="skinClothMapThickness" type="F32">1</value>
          <value name="skinClothMapOffset" type="F32">{skinClothMapOffset}</value>
          <array name="tetraMap" size="0" type="Struct" structElements="vertexBary(Vec3),tetraIndex0(U32),normalBary(Vec3)"></array>
          <value name="renderMeshAssetSorting" type="U32">2</value>
          <array name="physicsSubmeshPartitioning" size="{numPhysicsSubmeshPartitioning}" type="Struct" structElements="graphicalSubmesh(U32),physicalSubmesh(U32),numSimulatedVertices(U32),numSimulatedVerticesAdditional(U32),numSimulatedIndices(U32)">
	        {physicsSubmeshPartitioning}
          </array>
        </struct>
      </value>'''