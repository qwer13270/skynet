<template>
  <div>
    <el-container>
      <!--    SideBar  -->
      <el-aside :width="asideWidth" style="min-height: 100vh; background-color: #001529">
        <div style="
                            height: 60px;
                            color: white;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                          ">
          <img src="@/assets/UCS-Logo.png" alt="" style="width: 120px; height: 60px" />
        </div>

        <el-menu :collapse="isCollapse" :collapse-transition="false" router background-color="#001529"
          text-color="rgba(255, 255, 255, 0.65)" active-text-color="#fff" style="border: none"
          :default-active="$route.path">
          <!-- Master Database Submenu -->
          <el-submenu index="1">
            <template slot="title">
              <i class="el-icon-menu"></i>
              <span>Master Database</span>
            </template>
            <el-menu-item index="/">
              <i class="el-icon-collection"></i>
              Master
            </el-menu-item>
            <el-menu-item index="/pending">
              <i class="el-icon-refresh"></i>
              Pending
            </el-menu-item>
            <el-menu-item-group title="History">
              <el-menu-item index="/edit">
                <i class="el-icon-edit"></i>
                Edit
              </el-menu-item>
              <el-menu-item index="/manual">
                <i class="el-icon-document"></i>
                Manual
              </el-menu-item>
            </el-menu-item-group>
          </el-submenu>
          <el-submenu index="2">
            <template slot="title">
              <i class="el-icon-menu"></i>
              <span>New Satellites</span>
            </template>
            <el-menu-item index="/new_crawler">
              <i class="el-icon-aim"></i>
              Crawler
            </el-menu-item>
            <el-menu-item index="/new_pending">
              <i class="el-icon-refresh"></i>
              Pending
            </el-menu-item>
            <el-menu-item-group title="History">
              <el-menu-item index="/new_edit">
                <i class="el-icon-edit"></i>
                Edit
              </el-menu-item>
              <el-menu-item index="/new_action">
                <i class="el-icon-time"></i>
                Action
              </el-menu-item>
            </el-menu-item-group>
          </el-submenu>
          <el-submenu index="3">
            <template slot="title">
              <i class="el-icon-menu"></i>
              <span>Duplicate Satellites</span>
            </template>
            <el-menu-item index="/duplicate_pending">
              <i class="el-icon-refresh"></i>
              Pending
            </el-menu-item>
          </el-submenu>
          <el-menu-item index="/ucs_removed">
            <i class="el-icon-delete"></i>
            UCS Removed
          </el-menu-item>
          <el-menu-item @click="logout">
            <i class="el-icon-switch-button"></i>
            <span slot="title">Logout</span>
          </el-menu-item>

        </el-menu>
      </el-aside>

      <el-container>
        <!--        Header-->
        <el-header>

          <el-breadcrumb style="margin-left: 20px">
            <el-breadcrumb-item>Welcome, {{ username }}!</el-breadcrumb-item>
          </el-breadcrumb>

          <!--          <i :class="collapseIcon" style="font-size: 26px" @click="handleCollapse"></i>-->
          <el-breadcrumb separator-class="el-icon-arrow-right" style="margin-left: 20px">
            <el-breadcrumb-item :to="{ path: '/' }">Pending Page</el-breadcrumb-item>
          </el-breadcrumb>

          <!-- Search input for satellite name -->
          <el-input v-model="searchQuery" placeholder="Search by Cospar"
            style="width: 300px; margin-left: 20px; margin-right: 20px">
          </el-input>
          Undo:
          <el-switch v-model="showUndoColumn" style="margin-left: 10px; margin-right: 10px" />
        </el-header>


        <!--        Main Page-->
        <el-main>
          <el-table :data="filteredData" style="width: 100%">
            <el-table-column fixed prop="full_name" label="full_name" width="150"></el-table-column>
            <el-table-column prop="official_name" label="official_name" width="150"></el-table-column>
            <el-table-column prop="cospar" label="cospar" width="150"></el-table-column>
            <el-table-column v-for="column in editColumns" :key="column" :prop="column" :label="column" width="200">
            </el-table-column>
            <el-table-column prop="data_status" label="data_status" width="350"></el-table-column>
            <el-table-column v-for="column in dynamicColumns" :key="column" :prop="column" :label="column" width="350">
            </el-table-column>
            <el-table-column prop="additional_source" label="additional_source" width="350"></el-table-column>
            <el-table-column fixed="right" prop="removal_reason" label="removal_reason" :filters="removalReasonFilters"
              :filter-method="filterHandler" filter-placement="bottom-start" width="150"></el-table-column>
            <el-table-column fixed="right" label="Delete" width="120">
              <template slot-scope="scope">
                <el-button type="danger" icon="el-icon-delete" size="mini" @click="removeRow(scope.$index, scope.row)">
                  Delete
                </el-button>
              </template>
            </el-table-column>
            <el-table-column fixed="right" label="Operations" width="120" v-if="showUndoColumn">
              <template slot-scope="scope">
                <el-button type="primary" icon="el-icon-refresh" size="mini" @click="unremoveRow(scope.row)">
                  Undo
                </el-button>
              </template>
            </el-table-column>

          </el-table>

          <!-- Removed Items Table -->
          <el-table :data="removedItems" style="width: 100%; margin-top: 30px;" v-if="removedItems.length > 0">
            <el-table-column fixed prop="full_name" label="full_name" width="150"></el-table-column>
            <el-table-column prop="official_name" label="official_name" width="150"></el-table-column>
            <el-table-column prop="cospar" label="cospar" width="150"></el-table-column>
            <el-table-column v-for="column in editColumns" :key="column" :prop="column" :label="column" width="200">
            </el-table-column>
            <el-table-column prop="data_status" label="data_status" width="350"></el-table-column>
            <el-table-column v-for="column in dynamicColumns" :key="column" :prop="column" :label="column" width="350">
            </el-table-column>
            <el-table-column prop="additional_source" label="additional_source" width="350"></el-table-column>
            <el-table-column fixed="right" prop="removal_reason" label="removal_reason" :filters="removalReasonFilters"
              :filter-method="filterHandler" filter-placement="bottom-start" width="150"></el-table-column>
            <el-table-column fixed="right" label="Operations" width="120">
              <template slot-scope="scope">
                <el-button type="primary" icon="el-icon-refresh" size="mini" @click="undoRemove(scope.$index, scope.row)">
                  Undo
                </el-button>
              </template>
            </el-table-column>
          </el-table>

        </el-main>

        <div style="display: flex; justify-content: center; align-items: center; margin-top: 30px; padding: 20px;">
          <el-button type="success" @click="publishChanges">Publish Changes</el-button>
        </div>
      </el-container>
      <!-- Section for publishing changes -->
    </el-container>
  </div>
</template>
  
<script>
import axios from "axios";
export default {
  data() {
    return {
      isCollapse: false,
      asideWidth: "200px",
      collapseIcon: "el-icon-s-fold",
      tableData: [],
      removedItems: [],
      searchQuery: '',
      username: '',
      columns: [], // This now includes all columns
      dynamicColumns: [],
      editColumns: [],
      showUndoColumn: false,
      removalReasonFilters: [
        { text: 'Non-operational', value: 'Non-operational', column: 'removal_reason' },
        { text: 'Re-entered', value: 'Re-entered', column: 'removal_reason' },
        { text: 'Others', value: 'Others', column: 'removal_reason' },
      ],
    };
  },
  mounted() {
    this.fetchRemovedSatellites();
    this.getUsername();
  },
  computed: {
    // Add a computed property for filtering data
    filteredData() {
      if (this.searchQuery) {
        return this.tableData.filter(item =>
          item.cospar.toLowerCase().includes(this.searchQuery.toLowerCase())
        );
      }
      return this.tableData;
    },
  },
  methods: {
    unremoveRow(row) {
      axios.post('http://localhost:8000/api/pending_unremove_satellite', { cospar: row.cospar })
        .then(response => {
          // Handle success
          this.$message({
            message: 'Satellite un-removed successfully',
            type: 'success',
            duration: 2000  // Message will disappear after 5000 milliseconds (5 seconds)
          });
          this.fetchRemovedSatellites();
          // You might want to refresh the table data here
        })
        .catch(error => {
          // Handle error
          console.error('Error un-removing the satellite:', error);
          this.$message({
            message: 'Failed to un-remove satellite.',
            type: 'error',
            duration: 2000  // Message will disappear after 5000 milliseconds (5 seconds)
          });
        });
    },
    filterHandler(value, row, column) {
      const property = column.property;
      return value === 'Others' ? row.removal_reason !== 'Non-operational' && row.removal_reason !== 'Re-entry' : row.removal_reason === value;
    },
    logout() {
      localStorage.removeItem('authToken'); // 清除本地存储中的 token
      this.$router.push('/login'); // 重定向到登录页面
    },
    getUsername() {
      // Retrieve the username from local storage
      this.username = localStorage.getItem('username');
      console.log("Retrieved username:", this.username);
    },
    async fetchRemovedSatellites() {
      try {
        const response = await axios.get("http://localhost:8000/api/removed");
        this.tableData = response.data;
        if (this.tableData.length > 0) {
          const allColumns = Object.keys(this.tableData[0]);
          this.dynamicColumns = allColumns.filter(col => col.startsWith('source'));
          this.manualColumns = ['additional_source', 'full_name', 'official_name', 'editing', 'country', 'data_status', 'removal_reason', 'cospar'];

          // Define editColumns as all columns that are not dynamic or manual
          this.editColumns = allColumns.filter(col =>
            !this.dynamicColumns.includes(col) && !this.manualColumns.includes(col)
          );
        }
        console.log(this.tableData);
      } catch (error) {
        console.error("There was an error fetching the data:", error);
      }
    },
    removeRow(index, row) {
      this.removedItems.push(row); // Add the row to the removed items
      this.tableData.splice(index, 1); // Remove the row from the main table
      // You may also want to handle the removal in your backend/database
    },
    undoRemove(index, row) {
      this.tableData.push(row); // Add the row back to the main table
      this.removedItems.splice(index, 1); // Remove the row from the removed items
      // You may also want to handle the restoration in your backend/database
    },
    tableRowClassName({ row, rowIndex }) {
      // Here, you can specify a condition to highlight rows that need attention
      if (rowIndex === 2) {
        return 'highlight-row';
      }
      return '';
    },
    publishChanges() {

      if (this.removedItems.length === 0) {
        this.$message({
          message: 'No changes to publish.',
          type: 'warning',
          duration: 2000  // Message will disappear after 5000 milliseconds (5 seconds)
        });

        return;
      }

      let updates = this.removedItems.map(item => ({
        cospar: item.cospar,
        reason: item.removal_reason || 'Unknown'  // Default to 'Unknown' if reason is not provided
      }));

      console.log(updates);

      // Send the updated items and publisher name to the backend for database update
      axios.post('http://localhost:8000/api/master_satellites_remove', {
        updates: updates,
        name: this.username // Include the username in the request payload
      })
        .then(response => {
          console.log(response.data);
          // Handle the response, e.g., show a success message
          this.$message({
            message: 'Changes have been published successfully.',
            type: 'success',
            duration: 2000  // Message will disappear after 5000 milliseconds (5 seconds)
          });


          // Clear the removedItems if they have been successfully published
          this.removedItems = [];
        })
        .catch(error => {
          console.error('There was an error publishing the changes:', error);
          // Handle the error, e.g., show an error message
          this.$message({
            message: 'Failed to publish changes.',
            type: 'error',
            duration: 2000  // Message will disappear after 5000 milliseconds (5 seconds)
          });
        });

    },
  },
};
</script>
  
<style>
.el-table {
  margin-top: 20px;
}

.el-menu--inline {
  background-color: #000c17 !important;
}

.el-menu--inline .el-menu-item {
  background-color: #000c17 !important;
  padding-left: 49px !important;
}

.el-menu-item:hover,
.el-submenu__title:hover {
  color: #fff !important;
}

.el-submenu__title:hover i {
  color: #fff !important;
}

.el-menu-item:hover i {
  color: #fff !important;
}

.el-menu-item.is-active {
  background-color: #1890ff !important;
  border-radius: 5px !important;
  width: calc(100% - 8px);
  margin-left: 4px;
}

.el-menu-item.is-active i,
.el-menu-item.is-active .el-tooltip {
  margin-left: -4px;
}

.el-menu-item {
  height: 40px !important;
  line-height: 40px !important;
}

.el-submenu__title {
  height: 40px !important;
  line-height: 40px !important;
}

.el-submenu .el-menu-item {
  min-width: 0 !important;
}

.el-menu--inline .el-menu-item.is-active {
  padding-left: 45px !important;
}

/*.el-submenu__icon-arrow {*/
/*  margin-top: -5px;*/
/*}*/

.el-aside {
  transition: width 0.3s;
  box-shadow: 2px 0 6px rgba(0, 21, 41, 0.35);
}

.logo-title {
  margin-left: 5px;
  font-size: 20px;
  transition: all 0.3s;
  /* 0.3s */
}

.el-header {
  box-shadow: 2px 0 6px rgba(0, 21, 41, 0.35);
  display: flex;
  align-items: center;
}

.no-transition-submenu .el-menu--collapse {
  transition: none !important;
}
</style>
  