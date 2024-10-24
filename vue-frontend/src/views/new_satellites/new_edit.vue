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
              justify-content: center;">
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
                        <el-breadcrumb-item :to="{ path: '/' }">Edit Record</el-breadcrumb-item>
                    </el-breadcrumb>

                    <!-- Search input for satellite name -->
                    <el-input v-model="searchQuery" placeholder="Search by Cospar" style="width: 300px; margin-left: 20px;">
                    </el-input>
                </el-header>

                <!--        Main Page-->
                <el-main>
                    <el-table :data="filteredData" style="width: 100%">
                        <el-table-column fixed prop="cospar" label="cospar"></el-table-column>
                        <el-table-column prop="column_name" label="Column Name"></el-table-column>
                        <el-table-column prop="old_value" label="Old Value"></el-table-column>
                        <el-table-column prop="new_value" label="New Value"></el-table-column>
                        <el-table-column prop="edited_by" label="Edited By"></el-table-column>
                        <el-table-column prop="edit_time" label="Edit Time"></el-table-column>
                    </el-table>
                </el-main>

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
            tableData: [],
            searchQuery: '',
            username: '',
        };
    },
    mounted() {
        this.fetchEditRecords();
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
        logout() {
            localStorage.removeItem('authToken'); // 清除本地存储中的 token
            this.$router.push('/login'); // 重定向到登录页面
        },
        getUsername() {
            // Retrieve the username from local storage
            this.username = localStorage.getItem('username');
            console.log("Retrieved username:", this.username);
        },
        async fetchEditRecords() {
            try {
                const response = await axios.get(
                    "http://localhost:8000/api/ucs_new/get-edit-records"

                );
                this.tableData = response.data;
                console.log(this.tableData);
            } catch (error) {
                console.error('Error fetching edit records:', error);
            }
        }
    }
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

.no-transition-submenu .el-menu--collapse {
    transition: none !important;
}
</style>
    