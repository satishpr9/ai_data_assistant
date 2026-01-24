import { Bar, Line, Pie } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, PointElement, LineElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, ArcElement, Title, Tooltip, Legend);

export const renderAssistantContent = (msg) => {
  if(!msg.success){
    return <div className="error-message"><p>❌ Error:</p><p>{msg.answer||msg.error}</p></div>;
  }

  if(msg.mode==='chart' && msg.chart){
    const { type, labels, data } = msg.chart;
    const chartData = { labels, datasets:[{label:msg.chart.label||'Dataset', data, backgroundColor:'rgba(54,162,235,0.5)', borderColor:'rgba(54,162,235,1)', borderWidth:1}] };
    const chartOptions = { responsive:true, plugins:{legend:{position:'top'}, title:{display:true, text:msg.chart.title||'Chart'}} };
    return <div className="chart-box">{type==='bar' && <Bar data={chartData} options={chartOptions}/>} {type==='line' && <Line data={chartData} options={chartOptions}/>} {type==='pie' && <Pie data={chartData} options={chartOptions}/>}</div>;
  }

  if(msg.mode==='aggregation'){
    return <div className="aggregation-box"><p>📈 <strong>Results</strong></p><p>{msg.answer}</p></div>;
  }

  return <div className="rag-box"><p>{msg.answer}</p></div>;
};
