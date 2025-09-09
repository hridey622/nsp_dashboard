"use client"

import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { ArrowLeft, Filter, Download, Table } from "lucide-react"

interface NSPData {
  application_id: string
  permanent_address: string
  district_name: string
  state_name: string
  gender: string
  category_name: string
  category_id: string
  pay_amt_state_shr: string
  pay_amt_centre_shr: string
  annual_family_income: string
  marital_status: string
  marital_status_name: string
  fresh_renewal: string
  c_institution_id: string
  institute_district: string
}

const COLORS = [
  "#6366f1", // Primary blue
  "#3b82f6", // Blue
  "#8b5cf6", // Purple
  "#06b6d4", // Cyan
  "#10b981", // Emerald
  "#f59e0b", // Amber
  "#ef4444", // Red
]

export function NSPDashboard() {
  const [data, setData] = useState<NSPData[]>([])
  const [loading, setLoading] = useState(true)
  const [processedData, setProcessedData] = useState<any>({})

  useEffect(() => {
    const fetchData = async () => {
      try {
        console.log("[v0] Starting data fetch...")
        const response = await fetch(
          "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/nsp_dashboard-NaUiRW9VKF0rKXBinizfBe1UCbxYgU.csv",
        )
        const csvText = await response.text()
        console.log("[v0] CSV data fetched, length:", csvText.length)

        const lines = csvText.split("\n")
        const headers = lines[0].split(",")
        console.log("[v0] Headers:", headers)

        const parsedData = lines
          .slice(1)
          .filter((line) => line.trim())
          .map((line) => {
            const values = line.split(",")
            const obj: any = {}
            headers.forEach((header, index) => {
              obj[header.trim()] = values[index]?.trim() || ""
            })
            return obj as NSPData
          })

        console.log("[v0] Parsed data length:", parsedData.length)
        console.log("[v0] Sample data:", parsedData.slice(0, 2))

        const processed = processData(parsedData)
        setProcessedData(processed)
        setData(parsedData)
      } catch (error) {
        console.error("[v0] Error fetching data:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const processData = (rawData: NSPData[]) => {
    // Convert numeric fields and handle missing values
    const cleanedData = rawData.map((item) => ({
      ...item,
      pay_amt_state_shr: Number.parseFloat(item.pay_amt_state_shr) || 0,
      pay_amt_centre_shr: Number.parseFloat(item.pay_amt_centre_shr) || 0,
      annual_family_income: Number.parseFloat(item.annual_family_income) || 0,
      total_scholarship:
        (Number.parseFloat(item.pay_amt_state_shr) || 0) + (Number.parseFloat(item.pay_amt_centre_shr) || 0),
    }))

    // Gender distribution
    const genderCounts = cleanedData.reduce(
      (acc, item) => {
        const gender = item.gender || "Unknown"
        acc[gender] = (acc[gender] || 0) + 1
        return acc
      },
      {} as Record<string, number>,
    )

    const genderData = Object.entries(genderCounts).map(([gender, count]) => ({
      name: gender === "M" ? "Male" : gender === "F" ? "Female" : gender,
      value: count,
      percentage: ((count / cleanedData.length) * 100).toFixed(1),
    }))

    // Category distribution
    const categoryCounts = cleanedData.reduce(
      (acc, item) => {
        const category = item.category_name || "Unknown"
        acc[category] = (acc[category] || 0) + 1
        return acc
      },
      {} as Record<string, number>,
    )

    const categoryData = Object.entries(categoryCounts)
      .map(([category, count]) => ({
        name: category,
        value: count,
        percentage: ((count / cleanedData.length) * 100).toFixed(1),
      }))
      .sort((a, b) => b.value - a.value)

    // State distribution (top 10)
    const stateCounts = cleanedData.reduce(
      (acc, item) => {
        const state = item.state_name || "Unknown"
        acc[state] = (acc[state] || 0) + 1
        return acc
      },
      {} as Record<string, number>,
    )

    const stateData = Object.entries(stateCounts)
      .map(([state, count]) => ({ name: state, value: count }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 10)

    // District distribution (top 10)
    const districtCounts = cleanedData.reduce(
      (acc, item) => {
        const district = item.district_name || "Unknown"
        acc[district] = (acc[district] || 0) + 1
        return acc
      },
      {} as Record<string, number>,
    )

    const districtData = Object.entries(districtCounts)
      .map(([district, count]) => ({ name: district, value: count }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 10)

    // Marital status distribution
    const maritalCounts = cleanedData.reduce(
      (acc, item) => {
        const status = item.marital_status_name || "Unknown"
        acc[status] = (acc[status] || 0) + 1
        return acc
      },
      {} as Record<string, number>,
    )

    const maritalData = Object.entries(maritalCounts).map(([status, count]) => ({
      name: status,
      value: count,
      percentage: ((count / cleanedData.length) * 100).toFixed(1),
    }))

    // Fresh vs Renewal
    const freshRenewalCounts = cleanedData.reduce(
      (acc, item) => {
        const type = item.fresh_renewal === "F" ? "Fresh" : item.fresh_renewal === "R" ? "Renewal" : "Unknown"
        acc[type] = (acc[type] || 0) + 1
        return acc
      },
      {} as Record<string, number>,
    )

    const freshRenewalData = Object.entries(freshRenewalCounts).map(([type, count]) => ({
      name: type,
      value: count,
      percentage: ((count / cleanedData.length) * 100).toFixed(1),
    }))

    // Funding analysis
    const totalStateShare = cleanedData.reduce((sum, item) => sum + item.pay_amt_state_shr, 0)
    const totalCentreShare = cleanedData.reduce((sum, item) => sum + item.pay_amt_centre_shr, 0)
    const totalFunding = totalStateShare + totalCentreShare

    const fundingData = [
      { name: "State Share", value: totalStateShare, percentage: ((totalStateShare / totalFunding) * 100).toFixed(1) },
      {
        name: "Centre Share",
        value: totalCentreShare,
        percentage: ((totalCentreShare / totalFunding) * 100).toFixed(1),
      },
    ]

    return {
      genderData,
      categoryData,
      stateData,
      districtData,
      maritalData,
      freshRenewalData,
      fundingData,
      totalApplications: cleanedData.length,
      totalFunding,
      avgScholarship: totalFunding / cleanedData.length,
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading NSP Dashboard...</p>
        </div>
      </div>
    )
  }

  const {
    genderData = [],
    categoryData = [],
    stateData = [],
    districtData = [],
    maritalData = [],
    freshRenewalData = [],
    fundingData = [],
    totalApplications = 0,
    totalFunding = 0,
  } = processedData

  console.log("[v0] Processed data:", processedData)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" className="text-blue-600">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Home
              </Button>
              <span className="text-sm text-gray-600">Filter applied</span>
            </div>
            <Button variant="outline" size="sm">
              <Filter className="h-4 w-4 mr-2" />
              Filter
            </Button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-6 py-6">
        {/* Top Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          {/* Total Students Card */}
          <Card className="bg-purple-100 border-purple-200">
            <CardContent className="p-6">
              <div className="flex items-center gap-2 mb-2">
                <div className="w-2 h-2 bg-purple-600 rounded-full"></div>
                <span className="text-sm font-medium text-purple-800">TOTAL STUDENTS</span>
              </div>
              <div className="text-3xl font-bold text-purple-900 mb-2">
                {(totalApplications / 10000000).toFixed(2)} Cr
              </div>
              <div className="text-sm text-purple-700">
                <div>
                  Total Boys: {((genderData.find((d) => d.name === "Male")?.value || 0) / 10000000).toFixed(2)} Cr
                </div>
                <div>
                  Total Girls: {((genderData.find((d) => d.name === "Female")?.value || 0) / 10000000).toFixed(2)} Cr
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Migration Type */}
          <Card className="bg-purple-50 border-purple-200">
            <CardContent className="p-4">
              <div className="text-center mb-2">
                <span className="text-sm font-medium text-purple-800">MIGRATION TYPE</span>
              </div>
              <div className="h-24 w-24 mx-auto">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={freshRenewalData} cx="50%" cy="50%" innerRadius={15} outerRadius={35} dataKey="value">
                      {freshRenewalData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index]} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="text-xs text-center mt-2">
                {freshRenewalData.slice(0, 2).map((item, index) => (
                  <div key={item.name} className="flex items-center justify-center gap-1">
                    <div className={`w-2 h-2 rounded-full`} style={{ backgroundColor: COLORS[index] }}></div>
                    <span>
                      {item.name}: {item.percentage}%
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* BPL Status */}
          <Card className="bg-purple-50 border-purple-200">
            <CardContent className="p-4">
              <div className="text-center mb-2">
                <span className="text-sm font-medium text-purple-800">BPL STATUS</span>
              </div>
              <div className="h-24 w-24 mx-auto">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={fundingData} cx="50%" cy="50%" innerRadius={15} outerRadius={35} dataKey="value">
                      {fundingData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index + 2]} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="text-xs text-center mt-2">
                {fundingData.map((item, index) => (
                  <div key={item.name} className="flex items-center justify-center gap-1">
                    <div className={`w-2 h-2 rounded-full`} style={{ backgroundColor: COLORS[index + 2] }}></div>
                    <span>
                      {item.name}: {item.percentage}%
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Socio Economic Breakdown */}
          <Card className="bg-purple-50 border-purple-200">
            <CardContent className="p-4">
              <div className="text-center mb-2">
                <span className="text-sm font-medium text-purple-800">SOCIO ECONOMIC BREAKDOWN</span>
              </div>
              <div className="h-24 w-24 mx-auto">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={categoryData.slice(0, 4)}
                      cx="50%"
                      cy="50%"
                      innerRadius={15}
                      outerRadius={35}
                      dataKey="value"
                    >
                      {categoryData.slice(0, 4).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index]} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="text-xs text-center mt-2">
                {categoryData.slice(0, 2).map((item, index) => (
                  <div key={item.name} className="flex items-center justify-center gap-1">
                    <div className={`w-2 h-2 rounded-full`} style={{ backgroundColor: COLORS[index] }}></div>
                    <span>
                      {item.name}: {item.percentage}%
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* School Location Movement */}
          <Card className="bg-purple-50 border-purple-200">
            <CardContent className="p-4">
              <div className="text-center mb-2">
                <span className="text-sm font-medium text-purple-800">SCHOOL LOCATION MOVEMENT</span>
              </div>
              <div className="h-24 w-24 mx-auto">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={maritalData} cx="50%" cy="50%" innerRadius={15} outerRadius={35} dataKey="value">
                      {maritalData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index + 1]} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="text-xs text-center mt-2">
                {maritalData.slice(0, 2).map((item, index) => (
                  <div key={item.name} className="flex items-center justify-center gap-1">
                    <div className={`w-2 h-2 rounded-full`} style={{ backgroundColor: COLORS[index + 1] }}></div>
                    <span>
                      {item.name.substring(0, 8)}: {item.percentage}%
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Charts Section */}
        <div className="space-y-8">
          {/* Top 10 From State */}
          <Card>
            <CardContent className="p-6">
              <div className="flex justify-between items-start mb-6">
                <div className="flex-1">
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">Top 10 From State</h2>
                  <p className="text-gray-600 mb-4">
                    Displays the top states with the highest outbound student migration, categorized by rural and urban
                    school locations.
                  </p>
                  <div className="mb-4">
                    <h3 className="font-semibold text-gray-800 mb-2">Actionable Benefit</h3>
                    <p className="text-gray-600">
                      Helps identify states with significant student outflow, enabling strategies to enhance local
                      education and retain both rural and urban students.
                    </p>
                  </div>
                  <div className="flex gap-3">
                    <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                      <Download className="h-4 w-4 mr-2" />
                      Export Data
                    </Button>
                    <Button size="sm" variant="outline">
                      <Table className="h-4 w-4 mr-2" />
                      View as Table
                    </Button>
                  </div>
                </div>
                <div className="flex-1 ml-8">
                  <div className="flex justify-end mb-4 gap-2">
                    <Button size="sm" className="bg-blue-600 text-white">
                      Top
                    </Button>
                    <Button size="sm" variant="outline">
                      Bottom
                    </Button>
                    <Button size="sm" className="bg-blue-600 text-white">
                      From State
                    </Button>
                    <Button size="sm" variant="outline">
                      To State
                    </Button>
                  </div>
                  <div className="h-96">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={stateData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} fontSize={12} />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="value" fill="#3b82f6" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="flex justify-center mt-4 gap-4">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-blue-600 rounded"></div>
                      <span className="text-sm">Rural</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-blue-400 rounded"></div>
                      <span className="text-sm">Urban</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Top 10 From District */}
          <Card>
            <CardContent className="p-6">
              <div className="flex justify-between items-start mb-6">
                <div className="flex-1">
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">Top 10 From District</h2>
                  <p className="text-gray-600 mb-4">
                    Highlights districts with the highest outbound migration of students, segmented by rural and urban
                    schools.
                  </p>
                  <div className="mb-4">
                    <h3 className="font-semibold text-gray-800 mb-2">Actionable Benefit</h3>
                    <p className="text-gray-600">
                      Identifies districts needing urgent intervention to improve local education infrastructure and
                      reduce student migration.
                    </p>
                  </div>
                  <div className="flex gap-3">
                    <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                      <Download className="h-4 w-4 mr-2" />
                      Export Data
                    </Button>
                    <Button size="sm" variant="outline">
                      <Table className="h-4 w-4 mr-2" />
                      View as Table
                    </Button>
                  </div>
                </div>
                <div className="flex-1 ml-8">
                  <div className="flex justify-end mb-4 gap-2">
                    <Button size="sm" className="bg-blue-600 text-white">
                      Top
                    </Button>
                    <Button size="sm" variant="outline">
                      Bottom
                    </Button>
                    <Button size="sm" className="bg-blue-600 text-white">
                      From District
                    </Button>
                    <Button size="sm" variant="outline">
                      To District
                    </Button>
                  </div>
                  <div className="h-96">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={districtData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} fontSize={12} />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="value" fill="#3b82f6" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="flex justify-center mt-4 gap-4">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-blue-600 rounded"></div>
                      <span className="text-sm">Rural</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 bg-blue-400 rounded"></div>
                      <span className="text-sm">Urban</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
