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
                    <!--          <i :class="collapseIcon" style="font-size: 26px" @click="handleCollapse"></i>-->
                    <el-breadcrumb style="margin-left: 20px">
                        <el-breadcrumb-item>Welcome, {{ username }}!</el-breadcrumb-item>
                    </el-breadcrumb>

                    <el-breadcrumb separator-class="el-icon-arrow-right" style="margin-left: 20px">
                        <el-breadcrumb-item>Removed Satellites</el-breadcrumb-item>
                    </el-breadcrumb>

                    <!-- Search input for satellite name -->
                    <el-input v-model="searchQuery" placeholder="Search by Cospar"
                        style="width: 300px; margin-left: 20px; margin-right: 20px">
                    </el-input>

                    Undo:
                    <el-switch v-model="showUndoColumn" style="margin-left: 10px; margin-right: 10px" />


                    <el-dropdown>
                        <el-button>
                            Filter Column<i class="el-icon-arrow-down el-icon--right"></i>
                        </el-button>
                        <el-dropdown-menu slot="dropdown">
                            <el-checkbox-group v-model="selectedColumns">
                                <el-checkbox label="un_registry_country">UN Registry Country</el-checkbox>
                                <el-checkbox label="operator_country">Operator Country</el-checkbox>
                                <el-checkbox label="operator">operator</el-checkbox>
                                <!-- Repeat for other columns -->
                            </el-checkbox-group>
                        </el-dropdown-menu>
                    </el-dropdown>
                </el-header>

                <!--        Main Page-->
                <el-main>
                    <el-table :data="filteredData" border style="width: 100%" :row-style="({ row }) =>
                        row.data_status === 1 ? { backgroundColor: '#ffe79f' } : {}
                        ">
                        <el-table-column fixed prop="full_name" label="full_name" width="150"></el-table-column>
                        <el-table-column prop="official_name" label="official_name" width="150"></el-table-column>
                        <el-table-column prop="cospar" label="cospar" width="150"></el-table-column>
                        <el-table-column prop="country" label="country" v-if="selectedColumns.includes('country')"
                            width="150">
                            <!-- copy template to if want edit function -->
                            <template slot-scope="scope">
                                <!-- Check if the row is not in editing mode -->
                                <div v-if="!scope.row.editing">{{ scope.row.country }}</div>
                                <!-- If the row is in editing mode, show the input with tooltip -->
                                <el-tooltip v-else class="item" effect="dark" :content="scope.row.country"
                                    placement="top-start">
                                    <el-input v-model="scope.row.country" size="mini"></el-input>
                                </el-tooltip>
                            </template>
                        </el-table-column>
                        <el-table-column v-for="column in editColumns" :key="column" :prop="column" :label="column"
                            width="200">
                            <template slot-scope="scope">
                                <div v-if="!scope.row.editing || !isEditable(column)">
                                    {{ scope.row[column] }}
                                </div>
                                <el-tooltip v-else class="item" effect="dark" :content="scope.row[column]"
                                    placement="top-start">
                                    <el-input v-model="scope.row[column]" size="mini"></el-input>
                                </el-tooltip>
                            </template>
                        </el-table-column>
                        <!-- Dynamically generated 'source' columns -->
                        <el-table-column v-for="column in dynamicColumns" :key="column" :prop="column" :label="column"
                            width="350">
                        </el-table-column>
                        <el-table-column prop="data_status" label="data_status" width="350"></el-table-column>
                        <el-table-column prop="additional_source" label="additional_source" width="350"></el-table-column>
                        <el-table-column prop="username" label="username" width="100"></el-table-column>
                        <el-table-column prop="removal_date" label="removal_date" width="150"></el-table-column>
                        <el-table-column fixed="right" prop="removal_reason" label="removal_reason"
                            :filters="removalReasonFilters" :filter-method="filterHandler" filter-placement="bottom-start"
                            width="150"></el-table-column>
                        <el-table-column fixed="right" prop="removal_source" label="removal_source"
                            :filters="removalSourceFilters" :filter-method="filterHandler" filter-placement="bottom-start"
                            width="150"></el-table-column>
                        <el-table-column fixed="right" label="Operations" width="120" v-if="showUndoColumn">
                            <template slot-scope="scope">
                                <el-button type="primary" icon="el-icon-refresh" size="mini"
                                    @click="unremoveRow(scope.row)">
                                    Undo
                                </el-button>
                            </template>
                        </el-table-column>
                        <!--<el-table-column prop="data_status" label="data_status" width="150"></el-table-column> -->
                    </el-table>
                </el-main>

                <el-pagination @size-change="handleSizeChange" @current-change="handlePageChange"
                    :current-page="currentPage" :page-sizes="[10, 20, 30, 40]" :page-size="pageSize"
                    layout="total, sizes, prev, pager, next, jumper" :total="totalItems">
                </el-pagination>

                <el-dialog title="Select a Reason for Deny" :visible.sync="isDenyModalVisible" width="30%">
                    <el-radio-group v-model="selectedOption">
                        <el-radio label="Re-entered">Re-entered</el-radio>
                        <el-radio label="Non-operational">Non-operational</el-radio>
                        <el-radio label="Others">Others</el-radio>
                    </el-radio-group>

                    <el-input v-if="selectedOption === 'Others'" v-model="otherReason"
                        placeholder="Please specify the reason"></el-input>

                    <span slot="footer" class="dialog-footer">
                        <el-button @click="isDenyModalVisible = false">Cancel</el-button>
                        <el-button type="primary" @click="confirmRemoval">Confirm</el-button>
                    </span>
                </el-dialog>

                <el-dialog title="Confirm Approval" :visible.sync="isApproveModalVisible" width="30%">
                    <p>Are you sure you want to approve this item?</p>
                    <span slot="footer" class="dialog-footer">
                        <el-button @click="isApproveModalVisible = false">Cancel</el-button>
                        <el-button type="primary" @click="confirmApproval">Confirm</el-button>
                    </span>
                </el-dialog>
            </el-container>
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
            editDialogVisible: false,
            backupRow: null,
            filtersActive: false,
            // TODO put all columns data_status
            selectedColumns: ["country", "owner_country", "owner"],
            searchQuery: "",
            username: "",
            showOperations: false,
            isDenyModalVisible: false,
            tempDenyRow: null, // Temporary storage for the row to be denied
            selectedOption: "",
            otherReason: "",
            currentPage: 1,
            totalItems: 0,
            pageSize: 10,
            columns: [], // This now includes all columns
            editColumns: [],
            dynamicColumns: [],
            isApproveModalVisible: false,
            showUndoColumn: false,
            tempApproveRow: null, // Temporary storage for the row to be approved
            removalReasonFilters: [
                { text: 'Non-operational', value: 'Non-operational', column: 'removal_reason' },
                { text: 'Re-entered', value: 'Re-entered', column: 'removal_reason' },
                { text: 'Others', value: 'Others', column: 'removal_reason' },
            ],
            removalSourceFilters: [
                { text: 'ucs_master', value: 'ucs_master', column: 'removal_source' },
                { text: 'ucs_new', value: 'ucs_new', column: 'removal_source' },
                // ... other filters for the second column
            ],
        };
    },
    mounted() {
        this.fetchRemovedSatellites();
        this.getUsername();
    },
    methods: {
        unremoveRow(row) {
            axios.post('http://localhost:8000/api/ucs_unremove_satellite', { id: row.id })
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
        isEditable(column) {
            const nonEditableColumns = ['cospar', 'source'];
            return !nonEditableColumns.includes(column);
        },
        logout() {
            localStorage.removeItem("authToken"); // 清除本地存储中的 token
            this.$router.push("/login"); // 重定向到登录页面
        },
        getUsername() {
            // Retrieve the username from local storage
            this.username = localStorage.getItem("username");
            console.log("Retrieved username:", this.username);
        },
        handleApprove(row) {
            this.tempApproveRow = row;
            this.isApproveModalVisible = true;
        },
        confirmApproval() {
            // TODO 
            if (this.tempApproveRow) {
                // Logic to push the approved row to the ucs_master database
                // For example, using an axios call to your backend API
                console.log(this.tempApproveRow)
                axios.post('/api/ucs_master/new_satellites_approve', { data: this.tempApproveRow })
                    .then(response => {
                        console.log('Item approved:', response);
                        // Additional logic after successful approval
                    })
                    .catch(error => {
                        console.error('Error approving item:', error);
                    });

                this.isApproveModalVisible = false;
            }
        },
        handleDeny(row) {
            this.tempDenyRow = row;
            this.isDenyModalVisible = true;
        },

        confirmRemoval() {
            if (this.tempDenyRow) {
                // Logic to push the denied row to the removed database
                // For example, using an axios call to your backend API
                axios.post('/api/removed/add', {
                    data: this.tempDenyRow,
                    reason: this.selectedOption === 'Others' ? this.otherReason : this.selectedOption
                })
                    .then(response => {
                        console.log('Item denied and removed:', response);
                        // Additional logic after successful removal
                    })
                    .catch(error => {
                        console.error('Error removing item:', error);
                    });

                this.isDenyModalVisible = false;
            }
        },

        async fetchRemovedSatellites() {
            const limit = 10;
            const page = this.currentPage;
            try {
                /* const response = await axios.get(
                  "http://localhost:8000/api/satellites_master?page=${page}&limit=${limit}"
                ); // replace with your Flask app URL
                this.tableData = response.data.map((row) => ({
                  ...row,
                  editing: false,
                }));*/
                axios.get(`http://localhost:8000/api/satellites_removed?page=${page}&limit=${this.pageSize}&search=${encodeURIComponent(this.searchQuery)}`)
                    .then(response => {
                        this.tableData = response.data.data.map(row => ({ ...row, editing: false }));
                        console.log("Table Data:", this.tableData);
                        this.totalItems = response.data.total_count;
                        // Extract column names from the first row of tableData
                        if (this.tableData.length > 0) {
                            const allColumns = Object.keys(this.tableData[0]);
                            this.dynamicColumns = allColumns.filter(col => col.startsWith('source'));
                            this.manualColumns = ['additional_source', 'full_name', 'official_name', 'editing', 'country', 'data_status', 'removal_reason', 'removal_source', 'username', 'removal_date', 'cospar'];

                            // Define editColumns as all columns that are not dynamic or manual
                            this.editColumns = allColumns.filter(col =>
                                !this.dynamicColumns.includes(col) && !this.manualColumns.includes(col)
                            );
                        }
                    })
                    .catch(error => console.error("Error:", error));

                console.log(this.tableData);
            } catch (error) {
                console.error("There was an error fetching the data:", error);
            }
        },
        handlePageChange(page) {
            this.currentPage = page;
            this.fetchRemovedSatellites();
        },
        handleSizeChange(newSize) {
            this.pageSize = newSize;
            this.fetchRemovedSatellites();
        },
        removeRow(index, row) {
            this.tableData.splice(index, 1); // Remove the row
            // You may also want to delete the row from your backend/database
        },
        tableRowClassName({ row, rowIndex }) {
            // Here, you can specify a condition to highlight rows that need attention
            if (rowIndex === 2) {
                return "highlight-row";
            }
            return "";
        },
        startEdit(row) {
            console.log("Starting edit on row:", row);
            this.backupRow = Object.assign({}, row);
            this.tableData.forEach(r => r.editing = false);
            row.editing = true;
        },
        saveEdit(row) {
            let edit_records = [];
            // Collect changes, excluding the 'editing' property
            for (const key in row) {
                if (key !== "editing" && row[key] !== this.backupRow[key]) {
                    let record = {
                        cospar: row.cospar, // Add the JCAT value here
                        column: key,
                        oldValue: this.backupRow[key],
                        newValue: row[key],
                        time: new Date().toISOString(), // ISO format time of the edit
                    };
                    edit_records.push(record);
                }
            }
            if (edit_records.length > 0) {
                // Send the edit records to the backend
                axios
                    .post("http://localhost:8000/api/edit-data", {
                        edit_records: edit_records,
                        name: this.username,
                    })
                    .then((response) => {
                        console.log("Edit records sent successfully", response);
                    })
                    .catch((error) => {
                        console.error("Error sending edit records", error);
                    });
            }
            // Clear the backup since changes are saved
            this.backupRow = null;
            row.editing = false;
        },
        cancelEdit(row) {
            // Restore the original data from the backup
            Object.assign(row, this.backupRow);
            row.editing = false;
        },
        filterHandler(value, row, column) {
            const property = column.property;
            if (property === 'removal_reason') {
                return value === 'Others' ? row.removal_reason !== 'Non-operational' && row.removal_reason !== 'Re-entry' : row.removal_reason === value;
            } else if (property === 'removal_source') {
                console.log(row.removal_source)
                console.log(value)
                return row.removal_source === value;
            }
        },
        toggleFilters() {
            this.filtersActive = !this.filtersActive;
            // Optionally, add logic here to apply or remove filters
        },
    },
    computed: {
        filteredData() {

            // Check if there's any data to filter
            if (!this.tableData || this.tableData.length === 0) {
                console.log("No data available to filter.");
                return [];
            }

            // Simplify the filter for debugging
            const result = this.tableData.filter(row => {
                console.log("Row Data:", row); // Log each row data

                // Debugging: Check if `full_name` is defined in the row
                if (!row.cospar) {
                }

                // Temporary simplified search filter
                const matchesSearch = !this.searchQuery || (row.cospar && row.cospar.toLowerCase().includes(this.searchQuery.toLowerCase()));

                return matchesSearch; // Only apply the search filter for now
            });
            return result;
        },
    },
    watch: {
        searchQuery(newQuery, oldQuery) {
            console.log('Search query changed from', oldQuery, 'to', newQuery);
            this.currentPage = 1; // Reset to the first page
            this.fetchRemovedSatellites(); // Fetch filtered data
        }
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

/* Style for the button container */
.operation-buttons {
    display: flex;
    flex-direction: column;
    /* Stack buttons vertically */
    align-items: flex-start;
    /* Align buttons to the start of the flex container */
}

/* Style for individual buttons */
.operation-button {
    margin-bottom: 8px;
    /* Add bottom margin to each button except the last one */
}

.operation-button:last-child {
    margin-bottom: 0;
    /* Remove bottom margin from the last button */
}

.el-button+.el-button {
    margin-left: 0px;
}

.el-dropdown {
    margin-left: auto;
}

.el-dropdown-menu {
    padding: 10px;
    /* Add some padding inside the dropdown */
    max-height: 300px;
    /* Set a max height */
    overflow-y: auto;
    /* Add scrollbar if content is too long */
    width: auto;
    /* Adjust width as needed */
}

/* Style for each checkbox in the dropdown */
.el-checkbox {
    display: block;
    /* Make each checkbox take up a full line */
    margin: 5px 0;
    /* Add some margin for spacing */
}

/* Style for the checkbox label */
.el-checkbox__label {
    font-size: 14px;
    /* Adjust font size as needed */
}

.el-table .cell {
    text-overflow: clip;
}

.el-radio-group {
    margin-bottom: 20px;
}

.el-button--small {
    margin: 5px;
}


/* Pagination Styles */
.el-pagination {
    margin-top: 20px;
    display: flex;
    justify-content: center;
    /* Center align the pagination control */
    padding: 10px 0;
    background: #f4f4f5;
    /* Light background for pagination area */
    border-top: 1px solid #ebeef5;
    /* Border top for separation */
}

/* Pagination button styling */
.el-pagination button {
    color: #1890ff;
    /* Primary color for buttons */
    margin: 0 5px;
    /* Spacing between buttons */
}

/* Active page number styling */
.el-pagination .el-pager li.active {
    background-color: #1890ff;
    color: #fff;
    border-color: #1890ff;
}

.no-transition-submenu .el-menu--collapse {
    transition: none !important;
}
</style>
  