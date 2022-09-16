templatePhysicalMesh = '''<value type="Ref" included="1" className="ClothingPhysicalMeshParameters" version="0.10" checksum="0xcffdb608 0x34772e05 0xb720e9cd 0xf962cbf8">      
        <struct name="">
          <struct name="physicalMesh">
	        <value name="numVertices" type="U32">{numVertices_PhysicalMesh}</value>
	        <value name="numIndices" type="U32">{numFaceIndices_PhysicalMesh}</value>
	        <value name="numBonesPerVertex" type="U32">4</value>
	        <array name="vertices" size="{numVertices_PhysicalMesh}" type="Vec3">
	          {vertices_PhysicalMesh}
	        </array>
	        <array name="normals" size="{numVertices_PhysicalMesh}" type="Vec3">
	          {normals_PhysicalMesh}
	        </array>
	        <array name="skinningNormals" size="{numVertices_PhysicalMesh}" type="Vec3">
	          {skinningNormals_PhysicalMesh}
	        </array>
	        <array name="constrainCoefficients" size="{numVertices_PhysicalMesh}" type="Struct" structElements="maxDistance(F32),collisionSphereRadius(F32),collisionSphereDistance(F32)">
	          {constrainCoefficients_PhysicalMesh}
	        </array>
	        <array name="boneIndices" size="{numBoneIndices_PhysicalMesh}" type="U16">
	          {boneIndices_PhysicalMesh}
	        </array>
	        <array name="boneWeights" size="{numBoneIndices_PhysicalMesh}" type="F32">
	          {boneWeights_PhysicalMesh}
	        </array>
	        <array name="optimizationData" size="{numOptimizationData}" type="U8">
	          {optimizationData}
	        </array>
	        <value name="hasNegativeBackstop" type="Bool">false</value>
	        <value name="isClosed" type="Bool">false</value>
	        <array name="indices" size="{numFaceIndices_PhysicalMesh}" type="U32">
	          {faceIndices_PhysicalMesh}
	        </array>
	        <value name="maximumMaxDistance" type="F32">{maximumMaxDistance}</value>
	        <value name="physicalMeshSorting" type="U32">1</value>
	        <value name="shortestEdgeLength" type="F32">{shortestEdgeLength}</value>
	        <value name="averageEdgeLength" type="F32">{averageEdgeLength}</value>
	        <value name="isTetrahedralMesh" type="Bool">false</value>
	        <value name="flipNormals" type="Bool">false</value>
          </struct>
          <array name="submeshes" size="{numSubMeshes_PhysicalMesh}" type="Struct" structElements="numIndices(U32),numVertices(U32),numMaxDistance0Vertices(U32)">
	        {subMeshes_PhysicalMesh}
          </array>
          <array name="physicalLods" size="{numPhysicalLods}" type="Struct" structElements="costWithoutIterations(U32),submeshId(U32),solverIterationScale(F32),maxDistanceReduction(F32)">
	        {physicalLods}
          </array>
          <array name="transitionUpB" size="0" type="Struct" structElements="vtxTetraBary(Vec3),vertexIndexPlusOffset(U32),nrmTetraBary(Vec3),faceIndex0(U32),tetraIndex(U32)"></array>
          <array name="transitionUp" size="0" type="Struct" structElements="vertexBary(Vec3),vertexIndex0(U32),normalBary(Vec3),vertexIndex1(U32),tangentBary(Vec3),vertexIndex2(U32),vertexIndexPlusOffset(U32)">
          </array>
          <value name="transitionUpThickness" type="F32">0</value>
          <value name="transitionUpOffset" type="F32">0</value>
          <array name="transitionDownB" size="0" type="Struct" structElements="vtxTetraBary(Vec3),vertexIndexPlusOffset(U32),nrmTetraBary(Vec3),faceIndex0(U32),tetraIndex(U32)"></array>
          <array name="transitionDown" size="0" type="Struct" structElements="vertexBary(Vec3),vertexIndex0(U32),normalBary(Vec3),vertexIndex1(U32),tangentBary(Vec3),vertexIndex2(U32),vertexIndexPlusOffset(U32)"></array>
          <value name="transitionDownThickness" type="F32">0</value>
          <value name="transitionDownOffset" type="F32">0</value>
          <value name="referenceCount" type="U32">1</value>
        </struct>
      </value>'''